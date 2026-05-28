import feedparser
import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .config import RSS_FEEDS, FOCUS_KEYWORDS, BREAKING_KEYWORDS
from .database import is_posted


@dataclass
class NewsItem:
    title: str
    summary: str
    url: str
    source: str
    category: str
    published: Optional[datetime] = None
    image_url: Optional[str] = None

    def is_relevant(self) -> bool:
        text = (self.title + " " + self.summary).lower()
        return any(kw in text for kw in FOCUS_KEYWORDS)

    def is_breaking(self) -> bool:
        text = self.title.lower()
        return any(kw in text for kw in BREAKING_KEYWORDS)


async def fetch_all_news(limit_per_feed: int = 5) -> list[NewsItem]:
    return await _fetch(limit_per_feed, skip_posted=True)


async def fetch_news_for_digest(limit_per_feed: int = 10) -> list[NewsItem]:
    return await _fetch(limit_per_feed, skip_posted=True)


async def _fetch(limit_per_feed: int, skip_posted: bool) -> list[NewsItem]:
    items: list[NewsItem] = []

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (compatible; NEURNewsBot/1.0)"},
    ) as client:
        for feed_cfg in RSS_FEEDS:
            try:
                resp = await client.get(feed_cfg["url"])
                parsed = feedparser.parse(resp.text)

                count = 0
                for entry in parsed.entries:
                    if count >= limit_per_feed:
                        break

                    url = entry.get("link", "")
                    if not url:
                        continue

                    if skip_posted and await is_posted(url):
                        continue

                    title = entry.get("title", "").strip()
                    summary = _extract_summary(entry)

                    published = None
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        try:
                            published = datetime(*entry.published_parsed[:6])
                        except Exception:
                            pass

                    items.append(
                        NewsItem(
                            title=title,
                            summary=summary,
                            url=url,
                            source=feed_cfg["name"],
                            category=feed_cfg["category"],
                            published=published,
                        )
                    )
                    count += 1

            except Exception as e:
                print(f"[news_fetcher] Error fetching {feed_cfg['name']}: {e}")

    items.sort(key=lambda x: x.published or datetime.min, reverse=True)
    return items


def _extract_summary(entry) -> str:
    for field in ("summary", "description", "content"):
        text = ""
        val = getattr(entry, field, None)
        if isinstance(val, list) and val:
            text = val[0].get("value", "")
        elif isinstance(val, str):
            text = val

        if text:
            clean = BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()
            if len(clean) > 30:
                return clean[:1500]

    return ""
