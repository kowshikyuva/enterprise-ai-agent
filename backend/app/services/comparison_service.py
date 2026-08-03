from app.services.gemini_service import generate_json


def detect_contradictions(question: str, findings: list[dict]) -> list[dict]:
    """Stage 6 & 8: Compare Evidence + Detect Contradictions.

    `findings` is a list of {"index": int, "content": str, "source_title": str}.
    Returns pairs of finding indices that disagree, with an explanation.
    """

    if len(findings) < 2:
        return []

    numbered = "\n".join(
        f'{f["index"]}. ({f["source_title"]}) {f["content"]}' for f in findings
    )

    prompt = f"""
You are comparing findings gathered from different sources to answer this
research question: "{question}"

Findings:
{numbered}

Identify pairs of findings above that directly CONTRADICT each other (state
opposing things), not merely different aspects of the topic. Most findings
will NOT contradict anything — only flag genuine disagreements.

Respond with ONLY a JSON array of objects, nothing else. Example:
[{{"finding_a": 1, "finding_b": 3, "explanation": "Finding 1 claims X while finding 3 claims the opposite of X."}}]

If there are no contradictions, respond with: []
"""

    result = generate_json(prompt, [])
    if not isinstance(result, list):
        return []

    valid_indices = {f["index"] for f in findings}
    cleaned = []
    for c in result:
        if not isinstance(c, dict):
            continue
        a, b = c.get("finding_a"), c.get("finding_b")
        if a in valid_indices and b in valid_indices and a != b and c.get("explanation"):
            cleaned.append({
                "finding_a": a,
                "finding_b": b,
                "explanation": str(c["explanation"]).strip(),
            })

    return cleaned
