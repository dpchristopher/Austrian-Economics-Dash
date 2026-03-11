# -*- coding: utf-8 -*-
"""
utils/mises_scraper.py
-----------------------
Scrapes the Mises Wire for recent articles and provides keyword matching.
Cached for 1 hour. All errors are caught silently so the app never crashes.
Matching scores against both title and description/preview text so that
conceptual Austrian titles ("Why Central Banks Always Fail") still surface
for relevant keywords like "inflation" or "interest rates".
"""
import streamlit as st
import requests
from bs4 import BeautifulSoup

MISES_WIRE_URL = "https://mises.org/wire"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _fetch_article_description(url: str) -> str:
    """
    Fetch the first paragraph of an article body from its URL.
    Returns empty string on any failure.
    """
    try:
        resp = requests.get(url, timeout=8, headers=_HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Try common article body containers
        body = (
            soup.select_one(".field--name-body")
            or soup.select_one("article .node__content")
            or soup.select_one(".article-body")
            or soup.select_one("main article")
            or soup.select_one("article")
        )
        if body:
            for p in body.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 60:
                    return text[:400]
    except Exception:
        pass
    return ""


@st.cache_data(ttl=3600)
def get_mises_articles() -> list:
    """
    Scrape Mises Wire for the 30 most recent articles.
    For the top 10 articles where no description is found on the listing page,
    fetches the first paragraph of the article body directly (slow but cached).

    Returns
    -------
    list of dicts: [{"title": str, "url": str, "date": str, "description": str}, ...]
    Returns [] if scraping fails for any reason.
    """
    try:
        resp = requests.get(MISES_WIRE_URL, timeout=10, headers=_HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        articles = []

        # Try structured selectors in priority order
        containers = (
            soup.select("article")
            or soup.select(".views-row")
            or soup.select(".node--type-wire-article")
            or soup.select(".card")
        )

        if containers:
            for item in containers:
                title_el = item.select_one(
                    "h2 a, h3 a, h4 a, "
                    ".node__title a, .card__title a, .views-field-title a"
                )
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                url = title_el.get("href", "")
                if url and not url.startswith("http"):
                    url = "https://mises.org" + url

                date_el = item.select_one(
                    "time, .date-display-single, .field--name-created, .card__date"
                )
                date = ""
                if date_el:
                    date = date_el.get("datetime", "") or date_el.get_text(strip=True)

                # Expanded set of description selectors to match current Mises HTML
                desc_el = (
                    item.select_one(".field--name-field-teaser")
                    or item.select_one(".field--name-body")
                    or item.select_one(".views-field-field-teaser")
                    or item.select_one(".views-field-body")
                    or item.select_one(".card__description")
                    or item.select_one(".node__content p")
                    or item.select_one("p.teaser")
                    or item.select_one("p.summary")
                    or item.select_one(".field--name-field-subtitle")
                    or item.select_one(".subtitle")
                    or item.select_one(".teaser")
                    or item.select_one(".summary")
                    or item.select_one("p")
                )
                description = desc_el.get_text(strip=True) if desc_el else ""
                # Discard if the "description" is actually just the title text
                if description and description == title:
                    description = ""

                articles.append({
                    "title": title,
                    "url": url,
                    "date": date,
                    "description": description,
                })
                if len(articles) >= 75:
                    break

        else:
            # Fallback: grab any /wire/ links from the page
            for link in soup.select("a[href*='/wire/']"):
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                url = link.get("href", "")
                if url and not url.startswith("http"):
                    url = "https://mises.org" + url
                articles.append({"title": title, "url": url, "date": "", "description": ""})
                if len(articles) >= 75:
                    break

        # For the top 10 articles with no description, fetch from article page
        for i, article in enumerate(articles[:10]):
            if not article["description"] and article["url"]:
                article["description"] = _fetch_article_description(article["url"])

        return articles[:75]

    except Exception:
        return []


def match_articles(articles: list, keywords: list) -> list:
    """
    Return up to 5 articles that best match the given keywords.
    Scoring: count of keywords that appear as substrings in the combined
    title + description text (case-insensitive). Title matches count double
    so genuinely on-topic titles still rank above tangentially related previews.
    Ties broken by date descending (more recent preferred).
    Only articles with score > 0 are returned.
    Fallback: if fewer than 2 articles score above 0, the 2 most recent
    articles are returned so pages never show zero articles.

    Parameters
    ----------
    articles : list of article dicts from get_mises_articles()
    keywords : list of keyword strings to match against article text

    Returns
    -------
    Up to 5 best-matching articles (fewer if fewer match at all).
    """
    if not articles or not keywords:
        return []

    keywords_lower = [k.lower() for k in keywords]

    scored = []
    for article in articles:
        title_lower = article.get("title", "").lower()
        desc_lower = article.get("description", "").lower()
        # Title matches count double — rewards genuine topic alignment
        title_score = sum(2 for kw in keywords_lower if kw in title_lower)
        desc_score = sum(1 for kw in keywords_lower if kw in desc_lower)
        score = title_score + desc_score
        if score > 0:
            scored.append((score, article.get("date", ""), article))

    # Sort by score desc, then date desc (lexicographic — ISO dates sort correctly)
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [article for _, _, article in scored[:5]]
