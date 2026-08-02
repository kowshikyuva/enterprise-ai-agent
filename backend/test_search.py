from app.services.search_service import search_web

results = search_web("How is AI transforming retail operations?")

print(f"Found {len(results)} results\n")

for i, result in enumerate(results, start=1):
    print("=" * 60)
    print(f"Result {i}")
    print("Title :", result.get("title"))
    print("URL   :", result.get("href"))
    print("Body  :", result.get("body"))
    print()