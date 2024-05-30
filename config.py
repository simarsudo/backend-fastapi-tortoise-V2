import os
from dotenv import load_dotenv


load_dotenv()
DEV_DB_URL = os.getenv("DEV_DB_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "localhost",
                "port": "5432",
                "user": POSTGRES_USER,
                "password": POSTGRES_PASSWORD,
                "database": "products",
            },
        },
        # "default": DEV_DB_URL,
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
