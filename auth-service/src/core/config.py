import os

from dotenv import load_dotenv
from logging import config as logging_config
from pydantic import Field
from pydantic_settings import BaseSettings

from core.logger import LOGGING


load_dotenv()

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field("project name", alias="PROJECT_NAME")

    pstg_user: str = Field("postgres_user", alias="POSTGRES_USER")
    pstg_password: str = Field("postgres_password", alias="POSTGRES_PASSWORD")
    pstg_host: str = Field("127.0.0.1", alias="POSTGRES_HOST")
    pstg_port: int = Field(5432, alias="POSTGRES_PORT")
    pstg_db_name: str = Field("postgres_db_name", alias="POSTGRES_DB")

    redis_host: str = Field("127.0.0.1", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")

    authjwt_secret_key: str = Field("secret", alias="SECRET")
    authjwt_access_token_expires: int = 3600
    authjwt_refresh_token_expires: int = 864000

    superrole_name: str = os.environ.get("SUPERROLE_NAME")
    superuser_uuid: str = os.environ.get("SUPERUSER_UUID")
    superrole_uuid: str = os.environ.get("SUPERROLE_UUID")

    roles_change_data: list = ["admin"]
    roles_view_data: list = ["admin", "manager"]

    jaeger_host: str = Field("localhost", alias="JAEGER_HOST")
    jaeger_port: int = Field(4317, alias="JAEGER_PORT")

    yandex_id: str = Field("yandex_id", alias="YANDEX_ID")
    yandex_secret: str = Field("yandex_secret", alias="YANDEX_SECRET")
    yandex_redirect: str = Field("yandex_redirect", alias="YANDEX_REDIRECT")

    enable_tracer: int = Field(1, alias="TRACER")


settings = Settings()
