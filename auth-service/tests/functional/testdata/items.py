import uuid


method_list = [
    # roles
    ("api/v1/roles/", "get", {}),
    ("api/v1/roles/create", "post", {"name": "test", "service": "test"}),
    (
        f"api/v1/roles/update/{str(uuid.uuid4())}",
        "post",
        {"name": "test", "service": "test"},
    ),
    (f"api/v1/roles/remove/{str(uuid.uuid4())}", "get", {}),
    # users
    ("api/v1/users/", "get", {}),
    (
        "api/v1/users/create",
        "post",
        {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        },
    ),
    (
        f"api/v1/users/update/{str(uuid.uuid4())}",
        "post",
        {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        },
    ),
    (f"api/v1/users/remove/{str(uuid.uuid4())}", "get", {}),
    ("api/v1/users/login_history", "get", {}),
    (f"api/v1/users/login_history/{str(uuid.uuid4())}", "get", {}),
    ("api/v1/users/set_role", "post", {"user_id": "test", "role_id": "test"}),
    ("api/v1/users/deprive_role", "post", {"user_id": "test", "role_id": "test"}),
    # auth
    ("api/v1/auth/refresh", "get", {}),
    ("api/v1/auth/logout", "get", {}),
    ("api/v1/auth/protected", "get", {}),
]
