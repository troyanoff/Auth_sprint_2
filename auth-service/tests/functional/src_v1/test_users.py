import pytest

from http import HTTPStatus

from ..settings import settings


access_token = ""
refresh_token = ""
created_role_uuid = ""
created_user_uuid = ""


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
async def test_get_users_list(
    make_get_request,
):
    global access_token
    global refresh_token
    path = "api/v1/users"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) == 1
    superuser = {
        "uuid": settings.superuser_uuid,
        "login": settings.superuser_login,
        "first_name": "super",
        "last_name": "user",
        "roles": [
            {
                "uuid": settings.superrole_uuid,
                "name": settings.superrole_name,
                "service": "auth",
            }
        ],
    }
    assert set(superuser).issubset(body[0])


@pytest.mark.asyncio
async def test_create_user(make_post_request):
    global access_token
    global refresh_token
    global created_user_uuid
    path = "api/v1/users/create"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {
        "login": "test",
        "password": "test",
        "first_name": "test",
        "last_name": "test",
    }
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    clean_data = {"login": "test", "first_name": "test", "last_name": "test"}
    assert set(clean_data).issubset(body)

    created_user_uuid = body["uuid"]


@pytest.mark.asyncio
async def test_update_user(make_post_request):
    global access_token
    global refresh_token
    global created_user_uuid
    path = f"api/v1/users/update/{created_user_uuid}"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {
        "login": "test_update",
        "password": "test_update",
        "first_name": "test_update",
        "last_name": "test_update",
    }
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    clean_data = {
        "login": "test_update",
        "first_name": "test_update",
        "last_name": "test_update",
    }
    assert set(clean_data).issubset(body)


@pytest.mark.asyncio
async def test_get_user_login_history(
    make_get_request,
):
    global access_token
    global refresh_token
    path = "api/v1/users/login_history"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)


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
async def test_set_role_user(make_post_request):
    global access_token
    global refresh_token
    global created_user_uuid
    global created_role_uuid
    path = "api/v1/users/set_role"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {"user_id": created_user_uuid, "role_id": created_role_uuid}
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    roles = body.get("roles", False)
    assert roles
    assert isinstance(roles, list)
    assert roles[0]["uuid"] == created_role_uuid


@pytest.mark.asyncio
async def test_deprive_role_user(make_post_request):
    global access_token
    global refresh_token
    global created_user_uuid
    global created_role_uuid
    path = "api/v1/users/deprive_role"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    data = {"user_id": created_user_uuid, "role_id": created_role_uuid}
    body, _, status = await make_post_request(path=path, body=data, headers=headers)
    assert status == HTTPStatus.OK
    roles = body.get("roles", False)
    assert roles is not False
    assert isinstance(roles, list)
    assert roles == []


@pytest.mark.asyncio
async def test_remove_user(make_get_request):
    global access_token
    global refresh_token
    global created_user_uuid
    path = f"api/v1/users/remove/{created_user_uuid}"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    _, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_get_users_list_after_remove(
    make_get_request,
):
    global access_token
    global refresh_token
    path = "api/v1/users"
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + access_token,
    }
    body, _, status = await make_get_request(path=path, headers=headers)
    assert status == HTTPStatus.OK
    assert isinstance(body, list)
    assert len(body) == 1
