import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="account/login", scheme_name="JWT")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 Days


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
            "models": [
                "aerich.models",
                "models",
            ],
            "default_connection": "default",
        }
    },
}


SIZE_IDS = {
    "s": 1,
    "m": 2,
    "l": 3,
    "xl": 4,
    "xxl": 5,
    "32": 6,
    "34": 7,
    "36": 8,
    "38": 9,
    "40": 10,
}
