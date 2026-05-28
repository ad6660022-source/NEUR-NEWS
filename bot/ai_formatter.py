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

BREAKING_SYSTEM_PROMPT = """Ты — редактор экстренных новостей Telegram-канала NEUR NEWS.
Пиши коротко, чётко, как настоящий репортёр с места событий.

Правила:
- Используй Telegram HTML-разметку: <b>жирный</b>, <i>курсив</i>
- Начинай строго с: 🔴 <b>СРОЧНО</b>
- Затем ЖИРНЫЙ заголовок
- 2-3 предложения — только факты, ничего лишнего
- Не более 500 символов
- НЕ добавляй хэштеги, источники, ссылки

Структура:
🔴 <b>СРОЧНО</b>

<b>{Заголовок}</b>

{Факты 2-3 предложения}"""

DIGEST_SYSTEM_PROMPT = """Ты — редактор новостного дайджеста Telegram-канала NEUR NEWS.
Тебе дают список новостей — нужно составить красивый дайджест.

Правила:
- Используй Telegram HTML-разметку: <b>жирный</b>, <i>курсив</i>
- Заголовок дайджеста уже задан, не меняй его
- Для каждой новости: номер + <b>заголовок</b> — одно живое предложение с сутью
- Одно предложение на новость — максимум 100 символов
- Никаких хэштегов, источников, лишних слов
- Пиши живо и интересно

Структура:
{header}

{1️⃣ <b>Заголовок</b> — суть в одном предложении
2️⃣ ...
...}"""

USER_TEMPLATE = """Источник: {source}
Категория: {category}
Заголовок: {title}
Содержание: {summary}

Создай пост."""

DIGEST_USER_TEMPLATE = """Новости для дайджеста:

{news_list}

Заголовок дайджеста: {header}

Составь дайджест."""

DIGEST_HEADERS = {
    "morning": "🌅 <b>ДОБРОЕ УТРО | NEUR NEWS</b>\n\nГлавные новости:",
    "evening": "🌆 <b>ИТОГИ ДНЯ | NEUR NEWS</b>\n\nЧто произошло сегодня:",
}

NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]


async def format_news(item: NewsItem, breaking: bool = False) -> str:
    emoji = CATEGORY_EMOJI.get(item.category, "📰")
    system = BREAKING_SYSTEM_PROMPT if breaking else SYSTEM_PROMPT

    user_msg = USER_TEMPLATE.format(
        source=item.source,
        category=item.category,
        title=item.title,
        summary=item.summary[:800] if item.summary else "Нет описания",
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[ai_formatter] Claude error: {e}")
        return _fallback_format(item, emoji, breaking)


async def format_digest(items: list[NewsItem], digest_type: str) -> str:
    header = DIGEST_HEADERS.get(digest_type, DIGEST_HEADERS["morning"])

    news_list = "\n".join(
        f"{i + 1}. {item.title} ({item.source})"
        for i, item in enumerate(items[:5])
    )

    user_msg = DIGEST_USER_TEMPLATE.format(news_list=news_list, header=header)

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
            system=DIGEST_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"[ai_formatter] Claude digest error: {e}")
        return _fallback_digest(items, header)


def _fallback_format(item: NewsItem, emoji: str, breaking: bool) -> str:
    if breaking:
        return f"🔴 <b>СРОЧНО</b>\n\n<b>{item.title}</b>\n\n{item.summary[:300] if item.summary else ''}"
    summary = item.summary[:400] if item.summary else ""
    return f"{emoji} <b>{item.category.upper()}</b>\n\n<b>{item.title}</b>\n\n{summary}"


def _fallback_digest(items: list[NewsItem], header: str) -> str:
    lines = [header, ""]
    for i, item in enumerate(items[:5]):
        lines.append(f"{NUMBERS[i]} <b>{item.title}</b>")
    return "\n".join(lines)
