from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from ddgs import DDGS

BLOCKED_DOMAINS = [
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com"
]

# Hard timeout so a stalled DDG request fails loudly instead of hanging
# forever with no error and no log output.
SEARCH_TIMEOUT_SECONDS = 20

_executor = ThreadPoolExecutor(max_workers=4)


def _raw_search(query: str, max_results: int):
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=max_results))


def search_web(query: str, max_results: int = 10):
    try:
        future = _executor.submit(_raw_search, query, max_results)
        results = future.result(timeout=SEARCH_TIMEOUT_SECONDS)
    except FutureTimeoutError:
        print(f"Web search timed out after {SEARCH_TIMEOUT_SECONDS}s - skipping this query.")
        return []
    except Exception as e:
        print(f"Web search failed: {e}")
        return []