from app.services.gemini_service import generate_json


def generate_questions(topic: str, max_questions: int = 5) -> list[str]:
    """Stage 1: Define Research Questions.

    Decomposes a broad topic into a small set of focused, independently
    researchable sub-questions instead of dumping the raw topic straight
    into a search engine.
    """

    prompt = f"""
You are a research planning assistant.

Break the following broad research topic into {max_questions} specific,
independently researchable sub-questions. Each should be answerable using
web sources and should cover a different angle (e.g. use cases, benefits,
challenges/risks, adoption trends, real-world examples).

Topic: "{topic}"

Respond with ONLY a JSON array of strings, nothing else. Example:
["question 1", "question 2", "question 3"]
"""

    fallback = [topic]
    questions = generate_json(prompt, fallback)

    if not isinstance(questions, list) or not questions:
        return fallback

    # keep it a clean list of non-empty strings
    cleaned = [str(q).strip() for q in questions if str(q).strip()]
    return cleaned[:max_questions] or fallback
