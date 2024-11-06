from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import Depends

from db.postgres import get_session
from models.entity import User, Role
from schemas.users import UserSchema, UserRolesSchema, RoleSchema, SecondaryUserRole
from services.base import BaseCreate, BaseGetList, BaseUpdate, BaseRemove


class UsersService(BaseCreate, BaseGetList, BaseUpdate, BaseRemove):
    db_table = User
    return_model_create = UserSchema
    return_model_list = UserRolesSchema
    return_model_update = UserSchema
    db_table_right = Role
    return_model_secondary = UserRolesSchema

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self, limit: int, offset: int) -> list[UserRolesSchema]:
        query = (
            select(self.db_table)
            .limit(limit)
            .offset(offset)
            .options(joinedload(self.db_table.roles))
        )
        data = await self.session.execute(query)
        objs = data.scalars().unique()
        result = []
        for obj in objs:
            dict_obj = obj.__dict__
            roles = []
            for role in dict_obj["roles"]:
                roles.append(RoleSchema(**role.__dict__))
            dict_obj["roles"] = roles
            result.append(self.return_model_list(**dict_obj))
        return result

    async def set_secondary(
        self, secondary_obj: SecondaryUserRole
    ) -> UserRolesSchema | str:
        result = await self.session.execute(
            select(self.db_table)
            .where(self.db_table.id == secondary_obj.user_id)
            .options(joinedload(self.db_table.roles))
        )
        user_obj = result.scalars().first()
        if not user_obj:
            return "Пользователь не найден"
        role_obj = await self.session.get(self.db_table_right, secondary_obj.role_id)
        if not role_obj:
            return "Роль не найдена"
        if role_obj in user_obj.roles:
            return "Пользователю уже присвоена эта роль"
        user_obj.roles.append(role_obj)
        await self.session.commit()

        dict_obj = user_obj.__dict__
        roles = []
        for role in dict_obj["roles"]:
            roles.append(RoleSchema(**role.__dict__))
        dict_obj["roles"] = roles

        return self.return_model_secondary(**dict_obj)

    async def deprive_secondary(
        self, secondary_obj: SecondaryUserRole
    ) -> UserRolesSchema | str:
        result = await self.session.execute(
            select(self.db_table)
            .where(self.db_table.id == secondary_obj.user_id)
            .options(joinedload(self.db_table.roles))
        )
        user_obj = result.scalars().first()
        if not user_obj:
            return "Пользователь не найден"
        role_obj = await self.session.get(self.db_table_right, secondary_obj.role_id)
        if not role_obj:
            return "Роль не найдена"
        if role_obj not in user_obj.roles:
            return "Пользователю не присвоена эта роль"
        user_obj.roles.remove(role_obj)
        await self.session.commit()

        dict_obj = user_obj.__dict__
        roles = []
        for role in dict_obj["roles"]:
            roles.append(RoleSchema(**role.__dict__))
        dict_obj["roles"] = roles

        return self.return_model_secondary(**dict_obj)


@lru_cache()
def get_users_service(db_session: AsyncSession = Depends(get_session)) -> UsersService:
    return UsersService(db_session)
