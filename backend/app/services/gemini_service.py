from google.genai import Client
from app.core.config import GOOGLE_API_KEY

client = Client(api_key=GOOGLE_API_KEY)


def generate_summary(text):

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
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Gemini Error:")
        print(e)
        return f"Error: {e}"