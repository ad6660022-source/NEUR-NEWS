import anthropic
from .config import ANTHROPIC_API_KEY
from .news_fetcher import NewsItem

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

CATEGORY_EMOJI = {
    "россия": "🇷🇺",
    "мир": "🌍",
    "политика": "🏛",
    "экономика": "💰",
    "технологии": "💻",
    "спорт": "⚽",
    "культура": "🎭",
    "наука": "🔬",
    "медицина": "🏥",
}

SYSTEM_PROMPT = """Ты — редактор новостного Telegram-канала NEUR NEWS.
Твоя задача — превращать сырые новости в красивые, живые посты.

Правила форматирования:
- Пиши на русском языке
- Используй Telegram HTML-разметку: <b>жирный</b>, <i>курсив</i>
- Начинай с эмодзи-заголовка (1-2 эмодзи + категория новости)
- Потом ЖИРНЫЙ заголовок новости
- Затем 2-3 живых предложения — раскрой суть, добавь контекст, сделай интересно
- СТРОГО не более 700 символов в итоговом тексте (включая теги)
- Никаких скучных канцеляризмов. Пиши ярко, как журналист.
- НЕ добавляй хэштеги
- НЕ добавляй источник и ссылку
- НЕ пиши ничего после основного текста

Структура поста:
{emoji} <b>{КАТЕГОРИЯ}</b>

<b>{Заголовок}</b>

{Текст 2-3 предложения}"""

USER_TEMPLATE = """Источник: {source}
Категория: {category}
Заголовок: {title}
Содержание: {summary}
URL: {url}

Создай красивый пост для Telegram-канала."""


async def format_news(item: NewsItem) -> str:
    emoji = CATEGORY_EMOJI.get(item.category, "📰")

    user_msg = USER_TEMPLATE.format(
        source=item.source,
        category=item.category,
        title=item.title,
        summary=item.summary[:800] if item.summary else "Нет описания",
        url=item.url,
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[ai_formatter] Claude error: {e}")
        return _fallback_format(item, emoji)


def _fallback_format(item: NewsItem, emoji: str) -> str:
    summary = item.summary[:400] if item.summary else ""
    return (
        f"{emoji} <b>{item.category.upper()}</b>\n\n"
        f"<b>{item.title}</b>\n\n"
        f"{summary}"
    )
