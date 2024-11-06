import aiohttp
import random
import string

from http import HTTPStatus
from fastapi import Depends, APIRouter, HTTPException, Request
from fastapi_limiter.depends import RateLimiter
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from datetime import datetime
from opentelemetry import trace
from urllib.parse import urlencode

from core.config import settings
from core.check_auth import check_roles, CustomError
from schemas.auth import (
    Login,
    LoginResponse,
    AccessToken,
    AuthURL,
    AuthToken,
    Success,
    CheckRoles,
    YandexResponse,
)
from schemas.login_history import LoginHistoryCreateSchema
from schemas.users import UserRolesSchema
from services.auth import AuthService, get_auth_service
from services.cache import CacheServise, get_cache_service
from services.users import UsersService, get_users_service
from services.login_history import LoginHistoryService, get_login_history_service
from schemas.users import UserCreateSchema


router = APIRouter()
auth_dep = AuthJWTBearer()


@AuthJWT.load_config
def get_config():
    return settings


@router.post("/login",
             dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def login(
    user: Login,
    request: Request,
    authorize: AuthJWT = Depends(auth_dep),
    auth_service: AuthService = Depends(get_auth_service),
    login_service: LoginHistoryService = Depends(get_login_history_service),
) -> LoginResponse:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)

    with tracer.start_as_current_span("get_user"):
        get_user = await auth_service.get(user)
    if not get_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Bad username or password"
        )

    subject = f"{get_user.login}"
    user_for_claims = get_user.model_dump(mode="json")
    claims = {"uuid": user_for_claims["uuid"], "roles": user_for_claims["roles"]}

    with tracer.start_as_current_span("create_login_history"):
        await login_service.create(LoginHistoryCreateSchema(user_id=get_user.uuid))

    with tracer.start_as_current_span("create_tokens"):
        access_token = await authorize.create_access_token(
            subject=subject, user_claims=claims
        )
        refresh_token = await authorize.create_refresh_token(
            subject=subject, user_claims=claims
        )

    with tracer.start_as_current_span("update_refresh_token"):
        await auth_service.update(get_user.uuid, refresh_token)
    span.end()
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/admin_login",
             dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def admin_login(
    user: Login,
    auth_service: AuthService = Depends(get_auth_service),
    login_service: LoginHistoryService = Depends(get_login_history_service),
) -> UserRolesSchema:
    get_user = await auth_service.get(user)
    if not get_user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Bad username or password"
        )
    await login_service.create(LoginHistoryCreateSchema(user_id=get_user.uuid))
    return get_user


@router.get("/refresh",
            dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def refresh(
    request: Request,
    authorize: AuthJWT = Depends(auth_dep),
    auth_service: AuthService = Depends(get_auth_service),
) -> AccessToken:
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    with tracer.start_as_current_span("check_token"):
        await authorize.jwt_refresh_token_required()
    refresh_token = request.headers["Authorization"].split(" ")[1]
    current_user = await authorize.get_raw_jwt(refresh_token)
    user_uuid = current_user["uuid"]
    with tracer.start_as_current_span("get_refresh_token"):
        refresh_token_user = await auth_service.get_refresh_token(user_uuid)
    if refresh_token != refresh_token_user:
        raise CustomError(
            status_code=HTTPStatus.UNAUTHORIZED,
            message="Ранее был зарегистрирован выход из системы.",
        )
    user_sub = current_user["sub"]
    claims = {"uuid": user_uuid, "roles": current_user["roles"]}
    with tracer.start_as_current_span("create_access_token"):
        new_access_token = await authorize.create_access_token(
            subject=user_sub, user_claims=claims
        )
    span.end()
    return AccessToken(access_token=new_access_token)


@router.get("/logout", status_code=HTTPStatus.NO_CONTENT,
            dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def logout(
    request: Request,
    authorize: AuthJWT = Depends(auth_dep),
    auth_service: AuthService = Depends(get_auth_service),
    cache: CacheServise = Depends(get_cache_service),
):
    request_id = request.headers.get("X-Request-Id")
    tracer = trace.get_tracer(__name__)
    span = tracer.start_span(__name__)
    span.set_attribute("http.request_id", request_id)
    await authorize.jwt_required()

    claims = await authorize.get_raw_jwt()
    token_id = claims["jti"]
    token_exp = claims["exp"]
    user_sub = claims["uuid"]
    # Выставление refresh_token=None

    with tracer.start_as_current_span("update_refresh_token"):
        await auth_service.update(user_sub, None)
    dt_to_unix = datetime.now().timestamp()
    with tracer.start_as_current_span("set_token_redis"):
        await cache.set_key(token_id, token_exp - int(dt_to_unix))
    span.end()


@router.post("/check_auth",
             dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def check_auth(
    body: CheckRoles,
    authorize: AuthJWT = Depends(auth_dep),
    cache: CacheServise = Depends(get_cache_service),
) -> Success:
    await check_roles(authorize, cache, body.roles)
    return Success(success=True)


@router.get("/network_login",
            dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def network_login(
    request: Request,
    network: str = 'yandex'
) -> AuthURL:
    url = "https://oauth.yandex.ru/authorize?"
    params = {
        "response_type": "token",
        "redirect_uri": "https://oauth.yandex.ru/verification_code",
        "client_id": settings.yandex_id,
    }
    auth_url = url + urlencode(params)
    return AuthURL(url=auth_url)


@router.post("/network_redirect",
             dependencies=[Depends(RateLimiter(times=10, seconds=1))])
async def network_redirect(
    body: AuthToken,
    network: str = 'yandex',
    auth_service: AuthService = Depends(get_auth_service),
    authorize: AuthJWT = Depends(auth_dep),
    login_service: LoginHistoryService = Depends(get_login_history_service),
    user_service: UsersService = Depends(get_users_service),
    cache: CacheServise = Depends(get_cache_service),
) -> LoginResponse:
    if network == 'yandex':
        user_info = await auth_service.get_yandex_token(body.token)
    else:
        raise CustomError(
            status_code=HTTPStatus.BAD_REQUEST,
            message="Выберете network из списка [yandex, ].",
        )
    if not user_info.login:
        letters = string.ascii_lowercase
        user_info.login = ''.join(random.choice(letters) for i in range(10))
        user = None
    else:
        user = await auth_service.get_by_login(user_info.login)
    if not user:
        user_model = UserCreateSchema(
            login=user_info.login,
            password="default",
            first_name=user_info.first_name,
            last_name=user_info.last_name,
        )
        user = await user_service.create(user_model)
    await auth_service.create_network(user.uuid, network)
    tokens = await auth_service.create_tokens(user, authorize)
    await auth_service.update(user.uuid, tokens.refresh_token)
    await login_service.create(LoginHistoryCreateSchema(user_id=user.uuid))
    return tokens
