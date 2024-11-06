import aiohttp
import json

from fastapi import Request, HTTPException
from http import HTTPStatus

from core.config import settings


async def check_auth_and_roles(request: Request, roles: list = []):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Bearer token not found"
        )
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(
        headers=request.headers, timeout=timeout
    ) as session:
        async with session.post(
            settings.auth_url + "/check_auth", data=json.dumps({"roles": roles})
        ) as response:
            status = response.status
            response = await response.json()
    if status == HTTPStatus.OK:
        return True
    else:
        raise HTTPException(status_code=status, detail=response)
