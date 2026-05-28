import logging
from aiogram import Bot
from aiogram.enums import ParseMode

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from .news_fetcher import fetch_all_news, fetch_news_for_digest
from .ai_formatter import format_news, format_digest
from .database import is_posted, mark_posted

logger = logging.getLogger("neur_news")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

FOOTER = '\n\n<a href="https://t.me/neur_vpn_bot">🆓 БЕСПЛАТНЫЙ VPN</a>'


async def post_one_news() -> bool:
    news_list = await fetch_all_news(limit_per_feed=5)

    # Сначала ищем релевантные новости (политика / экономика / технологии)
    relevant = [n for n in news_list if n.is_relevant()]
    candidates = relevant if relevant else news_list

    for item in candidates:
        if await is_posted(item.url):
            continue
        try:
            text = await format_news(item)
            await _send(text)
            await mark_posted(item.url, item.title)
            logger.info(f"[poster] Posted: {item.title[:60]}...")
            return True
        except Exception as e:
            logger.error(f"[poster] Failed to post '{item.title[:40]}': {e}")
            continue

    logger.info("[poster] No new news to post.")
    return False


async def post_digest(digest_type: str) -> bool:
    news_list = await fetch_news_for_digest(limit_per_feed=10)

    if not news_list:
        logger.info(f"[poster] No news for {digest_type} digest.")
        return False

    # Берём топ-5, предпочитая релевантные
    relevant = [n for n in news_list if n.is_relevant()]
    pool = relevant if len(relevant) >= 3 else news_list
    top5 = pool[:5]

    try:
        text = await format_digest(top5, digest_type)
        await _send(text)

        for item in top5:
            await mark_posted(item.url, item.title)

        logger.info(f"[poster] {digest_type.capitalize()} digest posted ({len(top5)} items).")
        return True
    except Exception as e:
        logger.error(f"[poster] Digest failed: {e}")
        return False


async def check_breaking_news() -> bool:
    news_list = await fetch_all_news(limit_per_feed=3)

    for item in news_list:
        if not item.is_breaking():
            continue
        if await is_posted(item.url):
            continue
        try:
            text = await format_news(item, breaking=True)
            await _send(text)
            await mark_posted(item.url, item.title)
            logger.info(f"[poster] BREAKING posted: {item.title[:60]}...")
            return True
        except Exception as e:
            logger.error(f"[poster] Breaking news failed: {e}")

    return False


async def _send(text: str):
    await bot.send_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=text + FOOTER,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
