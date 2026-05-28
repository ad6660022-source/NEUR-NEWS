import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

TIMEZONE = "Europe/Moscow"

FOCUS_KEYWORDS = [
    "политик", "президент", "правительство", "министр", "санкци", "выбор",
    "экономик", "рубл", "доллар", "нефть", "газ", "ввп", "инфляц", "бюджет", "банк",
    "технолог", "искусственный интеллект", "ии", "цифров", "it", "интернет", "космос",
    "война", "армия", "военн", "украин", "нато", "сша", "китай", "европ",
]

BREAKING_KEYWORDS = [
    "срочно", "экстренно", "взрыв", "атака", "катастроф", "убит", "арест",
    "ядерн", "ракет", "теракт", "чрезвычайн", "авиакатастроф", "землетрясен",
]

RSS_FEEDS = [
    {
        "url": "https://tass.ru/rss/v2.xml",
        "name": "ТАСС",
        "category": "россия",
    },
    {
        "url": "https://lenta.ru/rss/news",
        "name": "Лента.ру",
        "category": "россия",
    },
    {
        "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
        "name": "РБК",
        "category": "россия",
    },
    {
        "url": "https://russian.rt.com/rss",
        "name": "RT",
        "category": "мир",
    },
    {
        "url": "https://www.bbc.com/russian/index.xml",
        "name": "BBC Россия",
        "category": "мир",
    },
]
