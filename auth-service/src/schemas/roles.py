from pydantic import BaseModel, Field

from schemas.base import MyBaseModel

# from schemas.users import UserSchema


class RoleCreateSchema(BaseModel):
    name: str = Field(max_length=32)
    service: str = Field(max_length=32)


class RoleUpdateSchema(BaseModel):
    name: str | None = Field(max_length=32, default=None)
    service: str | None = Field(max_length=32, default=None)


class RoleSchema(MyBaseModel):
    name: str = Field(max_length=32)
    service: str = Field(max_length=32)


# class RoleUsersSchema(RoleSchema):
#     users: list[UserSchema] = []
