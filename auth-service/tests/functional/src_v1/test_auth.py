import pytest

from http import HTTPStatus

from ..settings import settings


access_token = ""
refresh_token = ""


@pytest.mark.asyncio
async def test_login(make_post_request):
    global access_token
    global refresh_token
    path = "api/v1/auth/login"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }
    body = {"login": settings.superuser_login, "password": settings.superuser_password}
    body, _, status = await make_post_request(path=path, body=body, headers=headers)
    assert status == HTTPStatus.OK
    assert "access_token" in body
    assert "refresh_token" in body

    access_token = body["access_token"]
    refresh_token = body["refresh_token"]


@pytest.mark.asyncio
async def test_refresh(make_get_request):
    global access_token
    global refresh_token
    path = "api/v1/auth/refresh"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + refresh_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert "access_token" in body

    access_token = body["access_token"]


@pytest.mark.asyncio
async def test_logout(make_get_request):
    global access_token
    global refresh_token
    path = "api/v1/auth/logout"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_protected(make_get_request):
    global access_token
    global refresh_token
    path = "api/v1/auth/protected"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_refresh_before_logout(make_get_request):
    global access_token
    global refresh_token
    path = "api/v1/auth/refresh"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + refresh_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.UNAUTHORIZED
