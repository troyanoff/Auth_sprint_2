from pydantic import BaseModel


class Login(BaseModel):
    login: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshToken(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str


class AuthURL(BaseModel):
    url: str


class AuthToken(BaseModel):
    token: str


class Success(BaseModel):
    success: bool


class CheckRoles(BaseModel):
    roles: list = []


class YandexResponse(BaseModel):
    id: str
    login: str
    client_id: str
    display_name: str
    real_name: str
    first_name: str
    last_name: str
    sex: str
    default_email: str
    emails: list[str]
    birthday: str
    default_avatar_id: str
    is_avatar_empty: bool
    default_phone: dict
    psuid: str
