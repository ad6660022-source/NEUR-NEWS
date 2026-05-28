import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import TIMEZONE
from .database import init_db
from .poster import post_one_news, post_digest, check_breaking_news

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

    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    # Утренний дайджест — 07:00 МСК
    scheduler.add_job(
        lambda: post_digest("morning"),
        CronTrigger(hour=7, minute=0, timezone=TIMEZONE),
        id="morning_digest", name="Morning digest", replace_existing=True,
    )
    # Обычные посты — 10:00, 13:00, 22:00 МСК
    for hour in (10, 13, 22):
        scheduler.add_job(
            post_one_news,
            CronTrigger(hour=hour, minute=0, timezone=TIMEZONE),
            id=f"news_{hour}", name=f"News {hour}:00", replace_existing=True,
        )
    # Вечерний дайджест — 19:00 МСК
    scheduler.add_job(
        lambda: post_digest("evening"),
        CronTrigger(hour=19, minute=0, timezone=TIMEZONE),
        id="evening_digest", name="Evening digest", replace_existing=True,
    )
    # Проверка срочных новостей — каждые 30 минут
    scheduler.add_job(
        check_breaking_news,
        CronTrigger(minute="*/30", timezone=TIMEZONE),
        id="breaking_news", name="Breaking news check", replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started (TZ: {TIMEZONE}). "
        "Schedule: digest 07:00/19:00, news 10:00/13:00/22:00, breaking every 30min."
    )

    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
