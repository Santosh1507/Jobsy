from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from app.core.config import settings

Base = declarative_base()

async_engine = None
AsyncSessionLocal = None
sync_engine = None

def get_async_engine():
    global async_engine, AsyncSessionLocal
    if not settings.DATABASE_URL:
        return None, None
    if async_engine is None:
        DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        async_engine = create_async_engine(
            DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        AsyncSessionLocal = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    return async_engine, AsyncSessionLocal

def get_sync_engine():
    global sync_engine
    if not settings.DATABASE_URL:
        return None
    if sync_engine is None:
        sync_database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")
        sync_engine = create_engine(sync_database_url, echo=settings.DEBUG)
    return sync_engine


async def get_db():
    engine, SessionLocal = get_async_engine()
    if engine is None:
        yield None
    else:
        async with SessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()


async def init_db():
    engine, _ = get_async_engine()
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    engine, _ = get_async_engine()
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)