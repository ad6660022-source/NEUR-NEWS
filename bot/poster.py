from aiogram import Bot
from aiogram.enums import ParseMode

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from .news_fetcher import NewsItem, fetch_all_news
from .ai_formatter import format_news
from .image_fetcher import fetch_photo
from .database import is_posted, mark_posted

bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def post_one_news() -> bool:
    news_list = await fetch_all_news(limit_per_feed=5)

    for item in news_list:
        if await is_posted(item.url):
            continue

        try:
            text = await format_news(item)

            photo_url = item.image_url or await fetch_photo(item.title, item.category)
            await _send_with_photo(text, photo_url)

            await mark_posted(item.url, item.title)
            print(f"[poster] Posted: {item.title[:60]}...")
            return True

        except Exception as e:
            print(f"[poster] Failed to post '{item.title[:40]}': {e}")
            continue

    print("[poster] No new news to post.")
    return False


TELEGRAM_CAPTION_LIMIT = 1024


def _truncate(text: str, limit: int = TELEGRAM_CAPTION_LIMIT) -> str:
    if len(text) <= limit:
        return text
    truncated = text[:limit - 1]
    last_dot = truncated.rfind(".")
    return truncated[:last_dot + 1] if last_dot > limit // 2 else truncated


async def _send_with_photo(text: str, photo_url: str):
    try:
        await bot.send_photo(
            chat_id=TELEGRAM_CHANNEL_ID,
            photo=photo_url,
            caption=_truncate(text),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        print(f"[poster] Photo send failed ({e}), falling back to text only")
        await _send_text_only(text)


async def _send_text_only(text: str):
    await bot.send_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=False,
    )
