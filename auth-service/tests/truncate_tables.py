import psycopg2.extras
import os

from dotenv import load_dotenv

load_dotenv()


dsn = {
    "dbname": os.environ.get("POSTGRES_DB"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD"),
    "host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
    "port": os.environ.get("POSTGRES_PORT", 5432),
}


def truncate_all_tables(cursor: psycopg2.extensions.cursor):
    query = "TRUNCATE TABLE user_role, login_history, roles, users;"
    cursor.execute(query)


def main():
    with psycopg2.connect(**dsn) as conn, conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor
    ) as cursor:
        query = "TRUNCATE TABLE user_role, login_history, roles, users;"
        cursor.execute(query)
    conn.close()
    print("Таблицы очищены.")


if __name__ == "__main__":
    main()
