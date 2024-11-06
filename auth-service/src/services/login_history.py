from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends

from db.postgres import get_session
from models.entity import LoginHistory
from schemas.login_history import LoginHistorySchema, LoginHistoryCreateSchema
from services.base import BaseGetList, BaseCreate


class LoginHistoryService(BaseGetList, BaseCreate):
    db_table = LoginHistory
    return_model_list = LoginHistorySchema
    return_model_create = LoginHistoryCreateSchema

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(
        self, user_id: str, limit: int, offset: int
    ) -> list[LoginHistorySchema]:
        query = (
            select(self.db_table)
            .where(self.db_table.user_id == user_id)
            .limit(limit)
            .offset(offset)
        )
        data = await self.session.execute(query)
        objs = data.scalars().all()
        return [self.return_model_list(**obj.__dict__) for obj in objs]


@lru_cache()
def get_login_history_service(
    db_session: AsyncSession = Depends(get_session),
) -> LoginHistoryService:
    return LoginHistoryService(db_session)
