import psycopg2.extras
import os

from werkzeug.security import generate_password_hash
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()


dsn = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
}


def write_to_postgres_superrole(cursor: psycopg2.extensions.cursor):
    column_names = ["id", "name", "service"]
    column_names_str = ", ".join(column_names)
    bind_values = (os.environ.get("SUPERROLE_UUID"), "superrole", "auth")
    bind_values_str = str(bind_values)
    query = (
        f"INSERT INTO roles "
        f"({column_names_str}) VALUES {bind_values_str}"
        f"ON CONFLICT (id) DO NOTHING;"
    )
    cursor.execute(query)
    return dict(zip(column_names, bind_values))


def write_to_postgres_superuser(cursor: psycopg2.extensions.cursor):
    column_names = ["id", "login", "password", "first_name", "last_name", "created_at"]
    column_names_str = ", ".join(column_names)
    bind_values = (
        os.environ.get("SUPERUSER_UUID"),
        os.environ.get("SUPERUSER_LOGIN"),
        generate_password_hash(os.environ.get("SUPERUSER_PASSWORD")),
        "super",
        "user",
        str(datetime.now()),
    )
    bind_values_str = str(bind_values)
    query = (
        f"INSERT INTO users "
        f"({column_names_str}) VALUES {bind_values_str}"
        f"ON CONFLICT (id) DO NOTHING;"
    )
    cursor.execute(query)
    return dict(zip(column_names, bind_values))


def write_to_postgres_relation(cursor: psycopg2.extensions.cursor):
    column_names = ["user_id", "role_id"]
    column_names_str = ", ".join(column_names)
    bind_values = (os.environ.get("SUPERUSER_UUID"), os.environ.get("SUPERROLE_UUID"))
    bind_values_str = str(bind_values)
    query = (
        f"INSERT INTO user_role "
        f"({column_names_str}) VALUES {bind_values_str}"
        f"ON CONFLICT (user_id, role_id) DO NOTHING;"
    )
    cursor.execute(query)
    return dict(zip(column_names, bind_values))


def main():
    with psycopg2.connect(**dsn) as conn, conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor
    ) as cursor:
        superrole = write_to_postgres_superrole(cursor)
        superuser = write_to_postgres_superuser(cursor)
        relation = write_to_postgres_relation(cursor)

    conn.close()
    pprint(superrole)
    pprint(superuser)
    pprint(relation)
    print("Суперпользователь создан.")


if __name__ == "__main__":
    main()
