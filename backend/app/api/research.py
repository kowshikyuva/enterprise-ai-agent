from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research_service import run_research
from app.models.research_project import ResearchProject
from app.models.research_question import ResearchQuestion

router = APIRouter()


@router.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest, db: Session = Depends(get_db)):
    """Runs the full research pipeline for a new topic:
    define questions -> search -> collect -> store -> extract findings ->
    compare evidence -> classify -> detect contradictions -> conclude.
    """
    return run_research(request.topic, db)


@router.get("/research/{project_id}", response_model=ResearchResponse)
def get_research(project_id: int, db: Session = Depends(get_db)):
    """Re-fetches a previously completed research run from the stored
    knowledge base, without re-running the pipeline."""

    project = db.query(ResearchProject).filter(ResearchProject.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Research project not found")

    questions = (
        db.query(ResearchQuestion)
        .filter(ResearchQuestion.project_id == project_id)
        .order_by(ResearchQuestion.order)
        .all()
    )

    response_questions = []
    all_source_ids = set()

    for q in questions:
        for f in q.findings:
            all_source_ids.add(f.source_id)

        response_questions.append({
            "id": q.id,
            "text": q.text,
            "findings": [
                {
                    "id": f.id,
                    "content": f.content,
                    "classification": f.classification,
                    "confidence": f.confidence,
                    "source": {"id": f.source.id, "title": f.source.title, "url": f.source.url},
                }
                for f in q.findings
            ],
            "contradictions": [
                {
                    "finding_a_id": c.finding_a_id,
                    "finding_b_id": c.finding_b_id,
                    "explanation": c.explanation,
                }
                for c in q.contradictions
            ],
            "conclusion": {
                "summary": q.conclusion.summary if q.conclusion else "",
                "supporting_finding_ids": [f.id for f in q.conclusion.supporting_findings] if q.conclusion else [],
            },
        })

    final_report = project.results[-1].report if project.results else ""

    return {
        "project_id": project.id,
        "topic": project.topic,
        "status": project.status,
        "questions": response_questions,
        "total_sources": len(all_source_ids),
        "final_report": final_report,
    }
