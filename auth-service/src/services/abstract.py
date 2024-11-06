from abc import ABC, abstractmethod
from pydantic import BaseModel


class AbstractCreate(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def return_model_create(self, model: BaseModel):
        pass

    @abstractmethod
    async def create(self, fields: dict):
        pass


class AbstractGetById(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def return_model_get_by_id(self, model: BaseModel):
        pass

    @abstractmethod
    async def get_by_id(self, obj_id: str):
        pass


class AbstractGetList(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def return_model_list(self, model: BaseModel):
        pass

    @abstractmethod
    async def get_list(self, limit: int, offset: int):
        pass


class AbstractUpdateById(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def return_model_update(self, model: BaseModel):
        pass

    @abstractmethod
    async def update_by_id(self, obj_id: str, fields: BaseModel):
        pass


class AbstractRemoveById(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def remove_by_id(self, obj_id: str):
        pass


class AbstractGetUserAndUpdate(ABC):
    @abstractmethod
    async def db_table(self, model):
        pass

    @abstractmethod
    async def db_table_history(self, model):
        pass

    @abstractmethod
    async def return_model_login(self, model: BaseModel):
        pass

    @abstractmethod
    async def get(self, login: str, password: str):
        pass

    @abstractmethod
    async def update(self, obj, refresh_token: str):
        pass


class AbstractCreateSecondary:
    @abstractmethod
    async def db_secondary_table(self, model):
        pass

    @abstractmethod
    async def return_model_secondary(self, model: BaseModel):
        pass

    @abstractmethod
    async def set_secondary(self, left_obj_id: str, right_obj_id: str):
        pass


class AbstractGetByKey(ABC):
    @abstractmethod
    async def get_by_key(self, key: str, cache_expire: int):
        pass


class AbstractSetKey(ABC):
    @abstractmethod
    async def set_key(self, key: str, seconds: int):
        pass
