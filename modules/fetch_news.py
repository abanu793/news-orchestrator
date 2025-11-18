import requests
from modules import config
from urllib.parse import urlparse

RELIABLE_DOMAINS = ["thehindu.com", "bbc.com", "reuters.com", "cnn.com", "ndtv.com"]


def source_score(url):
    """
    Return simple reliability score for the source
    """
    domain = urlparse(url).netloc.replace("www.", "")
    return (
        5 if domain in RELIABLE_DOMAINS else 3
    )  # 5 = reliable, 3 = unknown/less reliable


def fetch_news(topic: str, page_size: int = None):
    if page_size is None:
        page_size = config.MAX_ARTICLES

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": topic,
        "apiKey": config.NEWS_API_KEY,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "publishedAt",
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])
        for a in articles:
            a["source_score"] = source_score(a.get("url", ""))
        return articles
    except requests.exceptions.RequestException:
        return []
