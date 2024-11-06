from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from pydantic import BaseModel

from db.postgres import get_session
from models.entity import Role
from schemas.roles import RoleSchema
from services.base import BaseCreate, BaseGetList, BaseUpdate, BaseRemove, BaseGetById


class RolesService(BaseCreate, BaseGetList, BaseUpdate, BaseRemove, BaseGetById):
    db_table = Role
    return_model_create: BaseModel = RoleSchema
    return_model_list: BaseModel = RoleSchema
    return_model_update: BaseModel = RoleSchema
    return_model_get_by_id: BaseModel = RoleSchema

    def __init__(self, session: AsyncSession):
        self.session = session


@lru_cache()
def get_roles_service(db_session: AsyncSession = Depends(get_session)) -> RolesService:
    return RolesService(db_session)
