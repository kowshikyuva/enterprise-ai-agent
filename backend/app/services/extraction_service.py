from app.services.gemini_service import generate_json

ALLOWED_CLASSIFICATIONS = {"benefit", "challenge", "trend", "statistic", "risk", "other"}


def extract_findings(question: str, source_title: str, source_url: str, content: str) -> list[dict]:
    """Stage 5 & 7: Extract Findings + Classify Findings.

    Pulls discrete, checkable claims out of one scraped source (instead of
    just concatenating raw text into one giant summary prompt), and tags
    each with a category and a confidence score.
    """

    trimmed = content[:4000]

    prompt = f"""
You are extracting factual findings from a single web source to help answer
a research question.

Research question: "{question}"
Source title: "{source_title}"
Source URL: {source_url}

Source content:
{trimmed}

Extract up to 4 distinct, specific findings from this source that are
directly relevant to the research question. Ignore boilerplate, navigation
text, or anything irrelevant. If the source has nothing relevant, return an
empty array.

For each finding provide:
- "content": one concise sentence stating the finding
- "classification": one of "benefit", "challenge", "trend", "statistic", "risk", "other"
- "confidence": a number 0.0-1.0 for how clearly the source supports this finding

Respond with ONLY a JSON array of objects, nothing else. Example:
[{{"content": "...", "classification": "trend", "confidence": 0.8}}]
"""

    findings = generate_json(prompt, [])

    if not isinstance(findings, list):
        return []

    cleaned = []
    for f in findings:
        if not isinstance(f, dict) or not f.get("content"):
            continue

        classification = str(f.get("classification", "other")).lower().strip()
        if classification not in ALLOWED_CLASSIFICATIONS:
            classification = "other"

        try:
            confidence = float(f.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))

        cleaned.append({
            "content": str(f["content"]).strip(),
            "classification": classification,
            "confidence": confidence,
        })

    return cleaned[:4]
