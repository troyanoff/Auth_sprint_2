import http
import json
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from config.settings import SECRETAUTH

User = get_user_model()


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        url = settings.AUTH_API_LOGIN_URL
        payload = {"login": username, "password": password}
        request_id = request.headers.get("X-Request-Id")
        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers={"X-Request-Id": request_id, "Content-Type": "application/json"},
            )
        except Exception:
            return None
        if response.status_code != http.HTTPStatus.OK:
            data = response.json()
            return None
        data = response.json()
        try:
            user, created = User.objects.get_or_create(
                id=data["id"],
            )
            user.login = data["login"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.set_password(password)
            roles = data["roles"]
            for i in roles:
                if i["name"] == "superrole":
                    user.is_admin = True
                    user.is_staff = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
