from http import HTTPStatus

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_limiter.depends import RateLimiter
from uuid import UUID
from opentelemetry import trace

from api.v1.auth import auth_dep
from core.check_auth import check_roles, check_services_and_roles
from core.config import settings
from services.cache import CacheServise, get_cache_service
from services.roles import RolesService, get_roles_service
from schemas.roles import RoleSchema, RoleCreateSchema, RoleUpdateSchema

router = APIRouter()


@router.get(
    "/",
    response_model=list[RoleSchema],
    response_model_by_alias=False,
    summary="Список ролей",
    description="Получить список ролей",
    response_description="Список ролей",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def roles(
    request: Request,
    limit: int = 20,
    offset: int = 0,
    role_service: RolesService = Depends(get_roles_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> list[RoleSchema]:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_roles"):
        await check_roles(authorize, cache, settings.roles_view_data)
    with tracer.start_as_current_span("get_list_roles"):
        roles_list = await role_service.get_list(limit, offset)
    span.end()
    return roles_list


@router.post(
    "/create",
    response_model=RoleSchema,
    response_model_by_alias=False,
    summary="Создание роли",
    description="Создать новую роль",
    response_description="Объект новой роли",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def create_role(
    body: RoleCreateSchema,
    request: Request,
    role_service: RolesService = Depends(get_roles_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> RoleSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_roles"):
        await check_services_and_roles(
            authorize, cache, settings.roles_change_data, body.service
        )
    if body.name == settings.superrole_name:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="invalid role name"
        )
    with tracer.start_as_current_span("create_role"):
        new_role = await role_service.create(body)
    if not new_role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Роль с таким name-service уже существует.",
        )
    span.end()
    return new_role


@router.post(
    "/update/{role_uuid}",
    response_model=RoleSchema,
    response_model_by_alias=False,
    summary="Обновить роль",
    description="Обновить данные роли",
    response_description="Объект обновленной роли",
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def update_role(
    role_uuid: UUID,
    body: RoleUpdateSchema,
    request: Request,
    role_service: RolesService = Depends(get_roles_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> RoleSchema:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_roles"):
        await check_roles(authorize, cache, settings.roles_change_data)
    if body.name == settings.superrole_name:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="invalid role name"
        )
    with tracer.start_as_current_span("get_role"):
        role = await role_service.get_by_id(role_uuid)
    await check_services_and_roles(
        authorize, cache, settings.roles_change_data, role.service
    )
    with tracer.start_as_current_span("update_by_id"):
        updated_role = await role_service.update_by_id(role_uuid, body)
    span.end()
    return updated_role


@router.get(
    "/remove/{role_uuid}",
    summary="Удалить роль",
    description="Удаление роли",
    status_code=HTTPStatus.NO_CONTENT,
    dependencies=[Depends(RateLimiter(times=10, seconds=1))]
)
async def remove_role(
    role_uuid: UUID,
    request: Request,
    role_service: RolesService = Depends(get_roles_service),
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> None:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_roles"):
        await check_roles(authorize, cache, settings.roles_change_data)
    with tracer.start_as_current_span("get_role"):
        role = await role_service.get_by_id(role_uuid)
    if role.name == settings.superrole_name:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="invalid remove role name"
        )
    await check_services_and_roles(
        authorize, cache, settings.roles_change_data, role.service
    )
    with tracer.start_as_current_span("remove_by_id"):
        removed = await role_service.remove_by_id(role_uuid)
    span.end()
    if not removed:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="role not found")
