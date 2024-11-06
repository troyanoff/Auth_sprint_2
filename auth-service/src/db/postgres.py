from core.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from typing import AsyncGenerator


Base = declarative_base()

dsn = (
    f"postgresql+asyncpg://{settings.pstg_user}:{settings.pstg_password}@"
    f"{settings.pstg_host}:{settings.pstg_port}/{settings.pstg_db_name}"
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(engine, class_=_AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[_AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
