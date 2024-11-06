import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    superrole_name: str = os.environ.get("SUPERROLE_NAME")
    superrole_uuid: str = os.environ.get("SUPERROLE_UUID")
    superuser_uuid: str = os.environ.get("SUPERUSER_UUID")
    superuser_login: str = os.environ.get("SUPERUSER_LOGIN")
    superuser_password: str = os.environ.get("SUPERUSER_PASSWORD")

    roles_change_data: list = ["admin"]
    roles_view_data: list = ["admin", "manager"]

    service_url: str = Field("http://localhost:8200", alias="AUTH_SERVICE_URL")


settings = Settings()
