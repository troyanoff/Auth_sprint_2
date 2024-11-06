from http import HTTPStatus
from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_limiter.depends import RateLimiter
from uuid import UUID
from opentelemetry import trace

from api.v1.auth import auth_dep
from core.check_auth import check_roles
from core.config import settings
from services.cache import CacheServise, get_cache_service
from services.login_history import LoginHistoryService, get_login_history_service
from services.users import UsersService, get_users_service
from schemas.users import (
    UserSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserRolesSchema,
    LoginHistorySchema,
    SecondaryUserRole,
)


router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRolesSchema],
    response_model_by_alias=False,
    summary="Список пользователей",
    description="Получить список пользователей",
    response_description="Список пользователей",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def roles(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> list[UserRolesSchema]:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_view_data)
    with tracer.start_as_current_span("get_list"):
        users_list = await user_service.get_list(limit, offset)
    span.end()
    return users_list


@router.post(
    "/create",
    response_model=UserSchema,
    response_model_by_alias=False,
    summary="Создание пользователя",
    description="Создать нового пользователя",
    response_description="Объект нового пользователя",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def create_user(
    body: UserCreateSchema,
    request: Request,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> UserSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_change_data)
    with tracer.start_as_current_span("create_user"):
        new_user = await user_service.create(body)
    if not new_user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Пользователь с таким login уже существует.",
        )
    span.end()
    return new_user


@router.post(
    "/update/{user_uuid}",
    response_model=UserSchema,
    response_model_by_alias=False,
    summary="Обновить данные пользователя",
    description="Обновить данные пользователя",
    response_description="Объект обновленной пользователя",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def update_user(
    user_uuid: UUID,
    body: UserUpdateSchema,
    request: Request,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> UserSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_change_data)
    with tracer.start_as_current_span("update_by_id"):
        updated_user = await user_service.update_by_id(user_uuid, body)
    span.end()
    return updated_user


@router.get(
    "/remove/{user_uuid}",
    summary="Удалить пользователя",
    description="Удаление пользователя",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def remove_role(
    user_uuid: UUID,
    request: Request,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> None:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_change_data)
    with tracer.start_as_current_span("remove_by_id"):
        removed = await user_service.remove_by_id(user_uuid)
    span.end()
    if not removed:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="role not found")


@router.get(
    "/login_history",
    response_model=list[LoginHistorySchema],
    response_model_by_alias=False,
    summary="История входов",
    description="Получить историю входов пользователя",
    response_description="Список времени входа",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def login_history_user_by_token(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    login_service: LoginHistoryService = Depends(get_login_history_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> list[LoginHistorySchema]:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    await check_roles(authorize, cache)
    with tracer.start_as_current_span("check_auth"):
        user_uuid = await check_roles(authorize, cache)
    with tracer.start_as_current_span("get_list"):
        history = await login_service.get_list(user_uuid, limit, offset)
    span.end()
    return history


@router.get(
    "/login_history/{user_uuid}",
    response_model=list[LoginHistorySchema],
    response_model_by_alias=False,
    summary="История входов",
    description="Получить историю входов пользователя",
    response_description="Список времени входа",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def login_history_user(
    user_uuid: UUID,
    request: Request,
    limit: int = 20,
    offset: int = 0,
    login_service: LoginHistoryService = Depends(get_login_history_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> list[LoginHistorySchema]:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_view_data)
    with tracer.start_as_current_span("get_list"):
        history = await login_service.get_list(user_uuid, limit, offset)
    span.end()
    return history


@router.post(
    "/set_role",
    response_model=UserRolesSchema,
    response_model_by_alias=False,
    summary="Назначить роль пользователю",
    description="Назначить роль пользователю",
    response_description="Созданное отношение",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def set_user_role(
    body: SecondaryUserRole,
    request: Request,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> UserRolesSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_change_data)
    if body.role_id == settings.superrole_uuid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="invalid role uuid"
        )
    with tracer.start_as_current_span("set_role"):
        updated_user = await user_service.set_secondary(body)
    if isinstance(updated_user, str):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=updated_user)
    span.end()
    return updated_user


@router.post(
    "/deprive_role",
    response_model=UserRolesSchema,
    response_model_by_alias=False,
    summary="Назначить роль пользователю",
    description="Назначить роль пользователю",
    response_description="Созданное отношение",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def deprive_user_role(
    body: SecondaryUserRole,
    request: Request,
    user_service: UsersService = Depends(get_users_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> UserRolesSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_auth"):
        await check_roles(authorize, cache, settings.roles_change_data)
    if body.role_id == settings.superrole_uuid:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="invalid role uuid"
        )
    with tracer.start_as_current_span("deprive_secondary"):
        updated_user = await user_service.deprive_secondary(body)
    if isinstance(updated_user, str):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=updated_user)
    span.end()
    return updated_user
