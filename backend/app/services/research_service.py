from app.services.search_service import search_web
from app.services.scraper_service import scrape_page
from app.services.gemini_service import generate_summary
from app.services.source_service import save_source
from app.services.chroma_service import add_document


def run_research(topic: str, db):

    # Search the web
    results = search_web(topic)

    sources = []
    combined_text = ""

    # Loop through search results
    for result in results:
        try:
            # Scrape webpage
            content = scrape_page(result["href"])

            # Skip empty pages
            if not content:
                continue

            # Save into PostgreSQL
            save_source(
                db=db,
                title=result["title"],
                url=result["href"],
                content=content
            )

            # Save into ChromaDB
            add_document(
                title=result["title"],
                url=result["href"],
                content=content
            )

            # Store for API response
            sources.append({
                "title": result["title"],
                "url": result["href"]
            })

            # Build context for Gemini
            combined_text += content[:2000] + "\n\n"

        except Exception as e:
            print(f"Error scraping {result['href']}: {e}")

    # Generate AI summary
    summary = generate_summary(combined_text)

    # Return response
    return {
        "topic": topic,
        "summary": summary,
        "total_sources": len(sources),
        "sources": sources
    }