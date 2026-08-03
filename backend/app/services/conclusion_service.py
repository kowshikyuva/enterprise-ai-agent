from app.services.gemini_service import generate_json


def generate_conclusion(question: str, findings: list[dict]) -> dict:
    """Stage 9: Generate Conclusions.

    `findings` is a list of {"index": int, "content": str}.
    Returns {"summary": str, "supporting_findings": [indices]} so the
    conclusion stays traceable to the specific findings that back it.
    """

    if not findings:
        return {
            "summary": "No sufficiently relevant findings were gathered to answer this question.",
            "supporting_findings": [],
        }

    numbered = "\n".join(f'{f["index"]}. {f["content"]}' for f in findings)

    prompt = f"""
You are writing a short, evidence-based conclusion for this research
question: "{question}"

Findings gathered from sources:
{numbered}

Write a 2-4 sentence conclusion that directly answers the question using
ONLY the findings above. Then list which finding numbers you actually relied
on.

Respond with ONLY a JSON object, nothing else. Example:
{{"summary": "...", "supporting_findings": [1, 2, 4]}}
"""

    fallback = {
        "summary": "Unable to synthesize a conclusion from the gathered findings.",
        "supporting_findings": [f["index"] for f in findings],
    }

    result = generate_json(prompt, fallback)
    if not isinstance(result, dict) or not result.get("summary"):
        return fallback

    valid_indices = {f["index"] for f in findings}
    supporting = [i for i in result.get("supporting_findings", []) if i in valid_indices]

    return {
        "summary": str(result["summary"]).strip(),
        "supporting_findings": supporting or [f["index"] for f in findings],
    }
