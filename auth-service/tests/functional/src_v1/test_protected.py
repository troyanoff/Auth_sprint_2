import pytest

from http import HTTPStatus

from ..testdata.items import method_list


@pytest.mark.parametrize("path, http_method, body", method_list)
@pytest.mark.asyncio
async def test_login(path, http_method, body, make_post_request, make_get_request):
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json",
    }
    if http_method == "get":
        body, _, status = await make_get_request(path=path, headers=headers)
    else:
        body, _, status = await make_post_request(path=path, body=body, headers=headers)
    assert status == HTTPStatus.UNAUTHORIZED
