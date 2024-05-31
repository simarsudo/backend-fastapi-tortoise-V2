import os
from dotenv import load_dotenv


load_dotenv()
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
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "models.user_models", "models.product_models"],
            "default_connection": "default",
        }
    },
}
