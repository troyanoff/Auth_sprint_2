from datetime import datetime
from pydantic import BaseModel, Field

from schemas.base import MyBaseModel
from schemas.roles import RoleSchema
from schemas.login_history import LoginHistorySchema


class UserCreateSchema(BaseModel):
    login: str = Field(max_length=32)
    password: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)


class UserUpdateSchema(BaseModel):
    login: str | None = Field(max_length=32, default=None)
    password: str | None = Field(max_length=32, default=None)
    first_name: str | None = Field(max_length=32, default=None)
    last_name: str | None = Field(max_length=32, default=None)


class UserSchema(MyBaseModel):
    login: str = Field(max_length=32)
    first_name: str = Field(max_length=32)
    last_name: str = Field(max_length=32)
    created_at: datetime


class UserRolesSchema(UserSchema):
    roles: list[RoleSchema] = []


class UserLoginsSchema(UserSchema):
    login_history: list[LoginHistorySchema] = []


class SecondaryUserRole(BaseModel):
    user_id: str
    role_id: str
