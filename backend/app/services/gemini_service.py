import json
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from google.genai import Client
from app.core.config import GOOGLE_API_KEY

client = Client(api_key=GOOGLE_API_KEY)

# Flash-Lite models consistently carry a much higher free-tier daily quota
# than full Flash models (often 1000+ RPD vs Flash's much lower ceiling,
# which varies by account/region). Since this pipeline is a multi-call
# workload, Lite is the better default here. If quality on findings
# extraction feels noticeably weaker, switch this back to "gemini-3.5-flash"
# once you have billing enabled (see note in README).
MODEL = "gemini-3.5-flash-lite"

# --- Rate limiting -----------------------------------------------------
# The Gemini free tier caps gemini-3.5-flash at 5 requests/minute. This
# pipeline makes many calls per research run (question decomposition,
# extraction per source, contradiction checks, conclusions), so without
# throttling it blows through that limit and every call after the 5th
# silently falls back to degraded content instead of raising.
#
# This keeps calls under the limit (with a safety margin) by waiting
# before any call that would exceed it, rather than firing and hoping.
MAX_CALLS_PER_WINDOW = 8
WINDOW_SECONDS = 60
MAX_RETRIES = 2

# Hard timeout on the underlying network call. Without this, a stalled
# connection (flaky network, DNS hiccup, blocked port) hangs forever with
# no error and no log output - it looks identical to "still working" from
# the outside. This forces it to fail loudly instead.
CALL_TIMEOUT_SECONDS = 30

_call_timestamps: list[float] = []
_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=4)


def _throttle():
    with _lock:
        now = time.monotonic()
        global _call_timestamps
        _call_timestamps = [t for t in _call_timestamps if now - t < WINDOW_SECONDS]

        if len(_call_timestamps) >= MAX_CALLS_PER_WINDOW:
            wait = WINDOW_SECONDS - (now - _call_timestamps[0]) + 1
        else:
            wait = 0

    if wait > 0:
        print(f"Rate limit guard: waiting {wait:.0f}s before next Gemini call...")
        time.sleep(wait)

    with _lock:
        _call_timestamps.append(time.monotonic())


def _extract_retry_delay(error_message: str) -> float:
    match = re.search(r"retry in (\d+(?:\.\d+)?)s", error_message, re.IGNORECASE)
    return float(match.group(1)) + 1 if match else 10.0


def _raw_call(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return response.text or ""


def _call_model(prompt: str) -> str:
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        _throttle()
        print(f"Calling Gemini ({MODEL})... [{prompt[:60].strip()}...]")

        try:
            future = _executor.submit(_raw_call, prompt)
            try:
                result = future.result(timeout=CALL_TIMEOUT_SECONDS)
                print("Gemini call finished.")
                return result
            except FutureTimeoutError:
                print(f"Gemini call timed out after {CALL_TIMEOUT_SECONDS}s - treating as failed, moving on.")
                raise TimeoutError(f"Gemini call exceeded {CALL_TIMEOUT_SECONDS}s")
        except Exception as e:
            last_error = e
            message = str(e)
            if "429" in message or "RESOURCE_EXHAUSTED" in message:
                if attempt < MAX_RETRIES:
                    delay = _extract_retry_delay(message)
                    print(f"Gemini rate-limited (attempt {attempt + 1}/{MAX_RETRIES + 1}), retrying in {delay:.0f}s...")
                    time.sleep(delay)
                    continue
            raise

    raise last_error


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