from ddgs import DDGS

BLOCKED_DOMAINS = [
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com"
]

def search_web(query: str, max_results: int = 10):
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    filtered = []

    for result in results:
        url = result.get("href", "").lower()

        if not any(domain in url for domain in BLOCKED_DOMAINS):
            filtered.append(result)

    return filtered[:5]