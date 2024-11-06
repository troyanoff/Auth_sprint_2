import pytest

from http import HTTPStatus

from ..settings import settings


access_token = ""
refresh_token = ""
created_role_uuid = ""


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
async def test_get_role_list(
    make_get_request,
):
    global access_token
    global refresh_token
    path = "api/v1/roles"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    superuser_role = {
        "uuid": settings.superrole_uuid,
        "name": settings.superrole_name,
        "service": "auth",
    }
    assert superuser_role in body


@pytest.mark.asyncio
async def test_create_role(make_post_request):
    global access_token
    global refresh_token
    global created_role_uuid
    path = "api/v1/roles/create"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {"name": "test", "service": "test"}
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    assert set(data).issubset(body)

    created_role_uuid = body["uuid"]


@pytest.mark.asyncio
async def test_update_role(make_post_request):
    global access_token
    global refresh_token
    global created_role_uuid
    path = f"api/v1/roles/update/{created_role_uuid}"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {"name": "test_update", "service": "test_update"}
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    assert set(data).issubset(body)


@pytest.mark.asyncio
async def test_remove_role(make_get_request):
    global access_token
    global refresh_token
    global created_role_uuid
    path = f"api/v1/roles/remove/{created_role_uuid}"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    _, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_get_role_list_after_remove(
    make_get_request,
):
    global access_token
    global refresh_token
    path = "api/v1/roles"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    superuser_role = {
        "uuid": settings.superrole_uuid,
        "name": settings.superrole_name,
        "service": "auth",
    }
    assert superuser_role in body
    assert len(body) == 1
