import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import POST_INTERVAL_HOURS
from .database import init_db
from .poster import post_one_news

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("neur_news")


async def main():
    logger.info("NEUR NEWS Bot starting...")
    await init_db()
    logger.info("Database initialized.")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        post_one_news,
        trigger=IntervalTrigger(hours=POST_INTERVAL_HOURS),
        id="post_news",
        name="Post news",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started. Posting every {POST_INTERVAL_HOURS} hours.")

    logger.info("Posting first news immediately...")
    await post_one_news()

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
