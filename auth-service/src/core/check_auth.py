from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException

from core.config import settings
from services.cache import CacheServise


class CustomError(AuthJWTException):
    """
    Ошибка при недоступности эндпоинта для ролей пользователя.
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


async def check_roles(
    authorize: AuthJWT, cache: CacheServise, allowed_roles: list = []
) -> bool:
    await authorize.jwt_required()
    claims = await authorize.get_raw_jwt()
    token_id = claims["jti"]
    logout_token = await cache.get_by_key(token_id)
    if logout_token:
        raise CustomError(
            status_code=401,
            message="Ранее был зарегистрирован выход из системы.",
        )

    user_roles = [role["name"] for role in claims["roles"]]
    user_uuid = claims["uuid"]
    if not allowed_roles:
        return user_uuid

    if settings.superrole_name in user_roles:
        return user_uuid

    for role in allowed_roles:
        if role in user_roles:
            return user_uuid

    raise CustomError(
        status_code=401,
        message="Данный ресурс не доступен для вашей роли.",
    )


async def check_services_and_roles(
    authorize: AuthJWT,
    cache: CacheServise,
    allowed_roles: list = [],
    service: str = None,
) -> bool:
    await authorize.jwt_required()
    claims = await authorize.get_raw_jwt()
    token_id = claims["jti"]
    logout_token = await cache.get_by_key(token_id)
    user_uuid = claims["uuid"]
    if logout_token:
        raise CustomError(
            status_code=401,
            message="Ранее был зарегистрирован выход из системы.",
        )
    user_roles = claims["roles"]
    user_roles_name = [role["name"] for role in user_roles]

    if not allowed_roles:
        return user_uuid
    if settings.superrole_name in user_roles_name:
        return user_uuid

    if service:
        for role in allowed_roles:
            if role in user_roles_name and role["service"] == service:
                return user_uuid

        raise CustomError(
            status_code=401,
            message="Данный ресурс не доступен для вашей роли или сервиса.",
        )

    for role in allowed_roles:
        if role in user_roles_name:
            return user_uuid

    raise CustomError(
        status_code=401,
        message="Данный ресурс не доступен для вашей роли.",
    )
