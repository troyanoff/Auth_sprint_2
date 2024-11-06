from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
from redis.asyncio import Redis
from werkzeug.security import generate_password_hash

from db.postgres import Base
from services import abstract as abs


class BaseGetById(abs.AbstractGetById):
    db_table = Base
    return_model_get_by_id = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, obj_id: str) -> BaseModel | None:
        obj = await self.session.get(self.db_table, obj_id)
        if not obj:
            return None
        return self.return_model_get_by_id(**obj.__dict__)


class BaseCreate(abs.AbstractCreate):
    db_table = Base
    return_model_create = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, fields: BaseModel):
        try:
            client = self.db_table(**fields.model_dump())
            self.session.add(client)
            await self.session.commit()
            return self.return_model_create(**client.__dict__)
        except IntegrityError:
            return None


class BaseGetList(abs.AbstractGetList):
    db_table = Base
    return_model_list = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_list(self, limit: int, offset: int) -> list[BaseModel]:
        data = await self.session.execute(
            select(self.db_table).limit(limit).offset(offset)
        )
        objs = data.scalars().unique()
        return [self.return_model_list(**obj.__dict__) for obj in objs]


class BaseUpdate(abs.AbstractUpdateById):
    db_table = Base
    return_model_update = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_by_id(self, obj_id: str, fields: BaseModel):
        obj = await self.session.get(self.db_table, obj_id)
        if not obj:
            return None
        for k, v in fields.model_dump().items():
            if k == "password":
                v = generate_password_hash(v)
            if v:
                setattr(obj, k, v)
        await self.session.commit()
        return self.return_model_update(**obj.__dict__)


class BaseRemove(abs.AbstractRemoveById):
    db_table = Base

    def __init__(self, session: AsyncSession):
        self.session = session

    async def remove_by_id(self, obj_id: str):
        obj = await self.session.get(self.db_table, obj_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.commit()
        return True


class BaseLogin(abs.AbstractGetUserAndUpdate):
    db_table = Base
    db_table_history = Base
    return_model_login = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user: BaseModel):
        result = await self.session.execute(
            select(self.db_table)
            .where(self.db_table.login == user.login)
            .options(joinedload(self.db_table.roles))
        )
        obj = result.scalars().first()
        print(obj)
        if not obj:
            return False
        if obj.check_password(user.password):
            return obj
        return False

    async def update(self, obj, refresh_token: str):
        obj.refresh_token = refresh_token
        await self.session.commit()
        history = self.db_table_history(user_id=obj.id)
        self.session.add(history)
        await self.session.commit()


class BaseGetByKey(abs.AbstractGetByKey):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get_by_key(self, key: str):
        value = await self.redis.get(key)
        return value


class BaseSetKey(abs.AbstractSetKey):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set_key(self, key: str, seconds: int):
        await self.redis.set(key, 1, seconds)
