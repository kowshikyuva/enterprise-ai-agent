import requests
from bs4 import BeautifulSoup


def scrape_page(url: str):

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        soup = BeautifulSoup(response.text, "lxml")

        paragraphs = soup.find_all("p")

        text = ""

        for p in paragraphs:
            text += p.get_text(" ", strip=True) + "\n"

        return text[:8000]

    except Exception as e:
        print(e)
        return ""