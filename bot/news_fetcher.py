import feedparser
import httpx
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from .config import RSS_FEEDS
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


async def fetch_all_news(limit_per_feed: int = 5) -> list[NewsItem]:
    items: list[NewsItem] = []

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
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

                    if await is_posted(url):
                        continue

                    title = entry.get("title", "").strip()
                    summary = _extract_summary(entry)
                    image_url = _extract_image(entry)

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
                            image_url=image_url,
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
            from bs4 import BeautifulSoup
            clean = BeautifulSoup(text, "html.parser").get_text(separator=" ").strip()
            if len(clean) > 30:
                return clean[:1500]

    return ""


def _extract_image(entry) -> Optional[str]:
    if hasattr(entry, "media_content") and entry.media_content:
        for m in entry.media_content:
            url = m.get("url", "")
            if url and any(url.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")):
                return url

    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("href", enc.get("url", ""))

    if hasattr(entry, "links"):
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href", "")

    return None
