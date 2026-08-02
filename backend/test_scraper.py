from app.services.search_service import search_web
from app.services.scraper_service import scrape_page

results = search_web("How is AI transforming retail operations?")

for i, r in enumerate(results):
    print(f"{i+1}. {r['title']}")
    print(r["href"])
    print()

url = results[0]["href"]

print("Scraping:", url)

content = scrape_page(url)

print(content[:3000])