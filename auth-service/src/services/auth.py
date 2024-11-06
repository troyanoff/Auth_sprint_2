import aiohttp

from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import Depends
from pydantic import BaseModel
from async_fastapi_jwt_auth import AuthJWT

from db.postgres import get_session
from models.entity import User, LoginNetwork
from schemas.auth import LoginResponse, Login, YandexResponse
from schemas.users import UserRolesSchema, RoleSchema, UserSchema
from services.base import BaseLogin


class AuthService(BaseLogin):
    db_table = User
    return_model_login: BaseModel = LoginResponse

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user: Login) -> UserRolesSchema | None:
        result = await self.session.execute(
            select(self.db_table)
            .where(self.db_table.login == user.login)
            .options(joinedload(self.db_table.roles))
        )
        obj = result.scalars().first()
        if not obj:
            return False
        if obj.check_password(user.password):
            dict_obj = obj.__dict__
            roles = []
            for role in dict_obj["roles"]:
                roles.append(RoleSchema(**role.__dict__))
            dict_obj["roles"] = roles
            return UserRolesSchema(**dict_obj)
        return False

    async def get_by_login(self, login: str) -> UserRolesSchema | None:
        result = await self.session.execute(
            select(self.db_table)
            .where(self.db_table.login == login)
            .options(joinedload(self.db_table.roles))
        )
        obj = result.scalars().first()
        if not obj:
            return None
        dict_obj = obj.__dict__
        roles = []
        for role in dict_obj["roles"]:
            roles.append(RoleSchema(**role.__dict__))
        dict_obj["roles"] = roles
        return UserRolesSchema(**dict_obj)

    async def update(self, user_id: str, refresh_token: str):
        obj = await self.session.get(self.db_table, user_id)
        obj.refresh_token = refresh_token
        await self.session.commit()

    async def get_refresh_token(self, obj_id: str) -> str | None:
        obj = await self.session.get(self.db_table, obj_id)
        if not obj:
            return None
        return obj.refresh_token

    async def get_yandex_token(self, token) -> YandexResponse:
        url = "https://login.yandex.ru/info"
        params = {"format": "json"}
        headers = {"Authorization": f"OAuth {token}"}
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, params=params) as response:
                response = await response.json()
        return YandexResponse(**response)

    async def create_network(self, user_uuid, network) -> None:
        result = await self.session.execute(
            select(LoginNetwork)
            .where(LoginNetwork.user_id == user_uuid,
                   LoginNetwork.network == network)
        )
        network_obj = result.scalars().first()
        if not network_obj:
            new_obj = LoginNetwork(user_id=user_uuid, network=network)
            self.session.add(new_obj)
            await self.session.commit()

    async def create_tokens(self, user: UserSchema, authorize: AuthJWT) -> YandexResponse:
        subject = f"{user.login}"
        user_for_claims = user.model_dump(mode="json")
        claims = {"uuid": user_for_claims["uuid"], "roles": user_for_claims["roles"]}

        access_token = await authorize.create_access_token(
            subject=subject, user_claims=claims
        )
        refresh_token = await authorize.create_refresh_token(
            subject=subject, user_claims=claims
        )
        return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@lru_cache()
def get_auth_service(db_session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(db_session)
