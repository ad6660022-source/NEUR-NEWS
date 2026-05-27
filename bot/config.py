import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", "2"))

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

HASHTAG_MAP = {
    "россия": ["#Россия", "#РФ", "#новости"],
    "мир": ["#МировыеНовости", "#Мир", "#новости"],
    "политика": ["#Политика", "#новости"],
    "экономика": ["#Экономика", "#Финансы"],
    "технологии": ["#Технологии", "#Tech"],
    "спорт": ["#Спорт"],
    "культура": ["#Культура"],
}
