import json
import re

from google.genai import Client
from app.core.config import GOOGLE_API_KEY

client = Client(api_key=GOOGLE_API_KEY)

MODEL = "gemini-3.5-flash"


def _call_model(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text or ""


def generate_summary(text: str) -> str:
    """Free-form markdown summary. Used by /chat and for the final report."""

    prompt = f"""
You are an Enterprise AI Research Assistant.

Analyze the following research and generate a professional report.

Research:
{text}

Rules:
- Use Markdown.
- Do NOT write long paragraphs.
- Use bullet points.
- Keep bullets short.

Format:

# Executive Summary

## Overview
- ...

## Key Findings
- ...
- ...

## Benefits
- ...
- ...

## Challenges
- ...
- ...

## Real-world Applications
- ...
- ...

## Conclusion
- ...
"""

    try:
        return _call_model(prompt)
    except Exception as e:
        print("Gemini Error:", e)
        return f"Error: {e}"


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```\s*$", "", text)
    return text.strip()


def generate_json(prompt: str, fallback):
    """Call Gemini and force-parse a JSON response.

    `fallback` is returned (instead of raising) if the model errors out or
    returns something unparsable, so a single bad LLM call never crashes the
    whole research pipeline run.
    """

    try:
        raw = _call_model(prompt)
        cleaned = _strip_json_fences(raw)
        return json.loads(cleaned)
    except Exception as e:
        print("Gemini JSON error:", e)
        return fallback
