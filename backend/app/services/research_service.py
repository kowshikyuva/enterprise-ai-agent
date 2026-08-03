from sqlalchemy.orm import Session

from app.services.search_service import search_web
from app.services.scraper_service import scrape_page
from app.services.source_service import save_source
from app.services.chroma_service import add_document
from app.services.question_service import generate_questions
from app.services.extraction_service import extract_findings
from app.services.comparison_service import detect_contradictions
from app.services.conclusion_service import generate_conclusion

from app.models.research_project import ResearchProject
from app.models.research_question import ResearchQuestion
from app.models.finding import Finding
from app.models.contradiction import Contradiction
from app.models.conclusion import Conclusion
from app.models.research_result import ResearchResult

SOURCES_PER_QUESTION = 2


def _compile_final_report(topic: str, question_results: list[dict]) -> str:
    lines = [f"# Executive Summary: {topic}", ""]

    for q in question_results:
        lines.append(f"## {q['text']}")
        lines.append(q["conclusion"].summary)

        if q["contradictions"]:
            lines.append("")
            lines.append("**Contradictions found:**")
            for c in q["contradictions"]:
                lines.append(f"- {c.explanation}")

        lines.append("")

    if not question_results:
        return "No findings were gathered."

    return "\n".join(lines)


def _research_one_question(db: Session, question: ResearchQuestion) -> dict:
    """Runs stages 2-9 for a single sub-question and persists everything."""

    search_results = search_web(question.text, max_results=SOURCES_PER_QUESTION + 2)

    # findings collected for this question, kept in a lightweight in-memory
    # shape ({"index", "content", "source_title"}) so the comparison /
    # conclusion prompts stay small, while the full Finding rows are
    # persisted to the DB for traceability.
    finding_rows: list[Finding] = []
    prompt_findings: list[dict] = []
    next_index = 1

    for result in search_results[:SOURCES_PER_QUESTION]:
        url = result.get("href")
        title = result.get("title", url)

        try:
            print(f"Scraping: {url}")
            content = scrape_page(url)
            if not content:
                print("  -> no usable content, skipping.")
                continue
            print(f"  -> scraped {len(content)} chars.")

            # Stage 3 & 4: Collect Information + Store Sources
            source = save_source(db=db, title=title, url=url, content=content)
            add_document(title=title, url=url, content=content)

            # Stage 5 & 7: Extract Findings + Classify Findings
            print("Extracting findings from this source...")
            extracted = extract_findings(question.text, title, url, content)
            print(f"  -> extracted {len(extracted)} findings.")

            for f in extracted:
                finding = Finding(
                    question_id=question.id,
                    source_id=source.id,
                    content=f["content"],
                    classification=f["classification"],
                    confidence=f["confidence"],
                )
                db.add(finding)
                db.flush()  # get finding.id without committing yet

                finding_rows.append(finding)
                prompt_findings.append({
                    "index": next_index,
                    "content": f["content"],
                    "source_title": title,
                    "finding_id": finding.id,
                })
                next_index += 1

        except Exception as e:
            print(f"Error researching source {url}: {e}")

    index_to_finding_id = {pf["index"]: pf["finding_id"] for pf in prompt_findings}

    # Stage 6 & 8: Compare Evidence + Detect Contradictions
    contradiction_rows = []
    if prompt_findings:
        raw_contradictions = detect_contradictions(question.text, prompt_findings)
        for c in raw_contradictions:
            fa_id = index_to_finding_id.get(c["finding_a"])
            fb_id = index_to_finding_id.get(c["finding_b"])
            if fa_id and fb_id:
                contradiction = Contradiction(
                    question_id=question.id,
                    finding_a_id=fa_id,
                    finding_b_id=fb_id,
                    explanation=c["explanation"],
                )
                db.add(contradiction)
                contradiction_rows.append(contradiction)

    # Stage 9: Generate Conclusions (+ Stage 10: Traceability via finding links)
    conclusion_data = generate_conclusion(question.text, prompt_findings)
    conclusion = Conclusion(question_id=question.id, summary=conclusion_data["summary"])
    supporting_ids = [index_to_finding_id[i] for i in conclusion_data["supporting_findings"] if i in index_to_finding_id]
    conclusion.supporting_findings = [f for f in finding_rows if f.id in supporting_ids]
    db.add(conclusion)

    db.flush()

    return {
        "id": question.id,
        "text": question.text,
        "findings": finding_rows,
        "contradictions": contradiction_rows,
        "conclusion": conclusion,
    }


def run_research(topic: str, db: Session) -> dict:
    project = ResearchProject(topic=topic, title=topic, status="running")
    db.add(project)
    db.flush()

    # Stage 1: Define Research Questions
    # Capped at 2 (rather than 5) so a full run stays fast: question gen +
    # 1 extraction call + up to 1 contradiction check + 1 conclusion call,
    # per question, is ~6-8 Gemini calls total instead of 14-20+.
    question_texts = generate_questions(topic, max_questions=2)

    question_results = []
    for order, text in enumerate(question_texts):
        print(f"\n=== Researching question {order + 1}/{len(question_texts)}: {text} ===")
        question = ResearchQuestion(project_id=project.id, text=text, order=order)
        db.add(question)
        db.flush()

        question_results.append(_research_one_question(db, question))

    total_sources = len({f.source_id for q in question_results for f in q["findings"]})

    # Compile the final executive report from the per-question conclusions
    # with plain string formatting - not another Gemini call. The conclusions
    # are already polished, evidence-backed text, so summarizing them again
    # through the LLM only adds latency/quota cost without adding value.
    final_report = _compile_final_report(topic, question_results)

    result_row = ResearchResult(project_id=project.id, report=final_report)
    db.add(result_row)

    project.status = "completed"
    db.commit()

    # Build the API response, refreshing each object for populated IDs.
    response_questions = []
    for q in question_results:
        db.refresh(q["conclusion"])
        response_questions.append({
            "id": q["id"],
            "text": q["text"],
            "findings": [
                {
                    "id": f.id,
                    "content": f.content,
                    "classification": f.classification,
                    "confidence": f.confidence,
                    "source": {"id": f.source.id, "title": f.source.title, "url": f.source.url},
                }
                for f in q["findings"]
            ],
            "contradictions": [
                {
                    "finding_a_id": c.finding_a_id,
                    "finding_b_id": c.finding_b_id,
                    "explanation": c.explanation,
                }
                for c in q["contradictions"]
            ],
            "conclusion": {
                "summary": q["conclusion"].summary,
                "supporting_finding_ids": [f.id for f in q["conclusion"].supporting_findings],
            },
        })

    return {
        "project_id": project.id,
        "topic": topic,
        "status": project.status,
        "questions": response_questions,
        "total_sources": total_sources,
        "final_report": final_report,
    }