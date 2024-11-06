from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

from schemas.base import MyBaseModel


class LoginHistorySchema(MyBaseModel):
    login_datetime: datetime


class LoginHistoryCreateSchema(BaseModel):
    user_id: str | UUID
