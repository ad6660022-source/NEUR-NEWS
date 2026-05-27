import hashlib
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, select


engine = create_async_engine("sqlite+aiosqlite:///news.db", echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class PostedNews(Base):
    __tablename__ = "posted_news"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    url: Mapped[str] = mapped_column(String(2048))
    title: Mapped[str] = mapped_column(String(512))
    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def _hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


async def is_posted(url: str) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(PostedNews).where(PostedNews.url_hash == _hash(url))
        )
        return result.scalar_one_or_none() is not None


async def mark_posted(url: str, title: str):
    async with SessionLocal() as session:
        session.add(PostedNews(url_hash=_hash(url), url=url, title=title))
        await session.commit()
