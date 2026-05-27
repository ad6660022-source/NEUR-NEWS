import httpx
import re
from typing import Optional

from .config import UNSPLASH_ACCESS_KEY

UNSPLASH_API = "https://api.unsplash.com/photos/random"

KEYWORD_TRANSLATIONS = {
    "россия": "russia",
    "москва": "moscow",
    "украина": "ukraine",
    "война": "war conflict",
    "экономика": "economy finance",
    "политика": "politics government",
    "выборы": "election vote",
    "технологии": "technology",
    "спорт": "sport",
    "культура": "culture art",
    "медицина": "medicine health",
    "наука": "science",
    "природа": "nature",
    "климат": "climate environment",
    "армия": "military army",
    "санкции": "sanctions economy",
    "нефть": "oil energy",
    "газ": "gas energy",
    "дипломатия": "diplomacy",
    "суд": "court justice",
    "мир": "world global",
}

FALLBACK_QUERIES = ["breaking news", "world news", "newspaper", "city skyline", "global"]


PICSUM_URL = "https://picsum.photos/1280/720"


async def fetch_photo(title: str, category: str) -> str:
    query = _build_query(title, category)

    for attempt_query in [query, "world news", "newspaper", "city"]:
        url = await _request_unsplash(attempt_query)
        if url:
            return url

    # Гарантированный фолбэк — всегда возвращает случайное HD фото
    return PICSUM_URL


def _build_query(title: str, category: str) -> str:
    text = (title + " " + category).lower()
    english_terms = []

    for ru_word, en_phrase in KEYWORD_TRANSLATIONS.items():
        if ru_word in text:
            english_terms.append(en_phrase)

    if not english_terms:
        english_terms = ["news", "world"]

    return " ".join(english_terms[:3])


async def _request_unsplash(query: str) -> Optional[str]:
    if not UNSPLASH_ACCESS_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                UNSPLASH_API,
                params={
                    "query": query,
                    "orientation": "landscape",
                    "content_filter": "high",
                },
                headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("urls", {}).get("regular")
    except Exception as e:
        print(f"[image_fetcher] Unsplash error: {e}")

    return None
