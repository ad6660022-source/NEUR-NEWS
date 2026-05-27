from aiogram import Bot
from aiogram.enums import ParseMode

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from .news_fetcher import fetch_all_news
from .ai_formatter import format_news
from .database import is_posted, mark_posted

bot = Bot(token=TELEGRAM_BOT_TOKEN)

FOOTER = '\n\n<a href="https://t.me/neur_vpn_bot">🆓 БЕСПЛАТНЫЙ VPN</a>'


async def post_one_news() -> bool:
    news_list = await fetch_all_news(limit_per_feed=5)

    for item in news_list:
        if await is_posted(item.url):
            continue

        try:
            text = await format_news(item)

            await bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=text + FOOTER,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

            await mark_posted(item.url, item.title)
            print(f"[poster] Posted: {item.title[:60]}...")
            return True

        except Exception as e:
            print(f"[poster] Failed to post '{item.title[:40]}': {e}")
            continue

    print("[poster] No new news to post.")
    return False
