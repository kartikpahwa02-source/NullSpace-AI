import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def search_web(query, num=5):
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for item in soup.select(".result__body")[:num]:
            title = item.select_one(".result__title")
            snippet = item.select_one(".result__snippet")
            results.append({
                "title": title.get_text(strip=True) if title else "",
                "snippet": snippet.get_text(strip=True) if snippet else "",
            })
        return results if results else [{"title": "No results", "snippet": ""}]
    except Exception as e:
        return [{"title": "Error", "snippet": str(e)}]

def fetch_page(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:4000]
    except Exception as e:
        return f"Error: {e}"