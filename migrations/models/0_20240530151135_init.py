from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "customer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "full_name" VARCHAR(50),
    "hashed_password" VARCHAR(128),
    "token" VARCHAR(128),
    "registered_on" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "address" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "address" VARCHAR(100) NOT NULL,
    "city" VARCHAR(20) NOT NULL,
    "state" VARCHAR(20) NOT NULL,
    "pinCode" VARCHAR(10) NOT NULL,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "employee" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "full_name" VARCHAR(50) NOT NULL,
    "phone_no" VARCHAR(10) NOT NULL,
    "is_disabled" BOOL NOT NULL  DEFAULT False,
    "hashed_password" VARCHAR(150) NOT NULL,
    "token" VARCHAR(200),
    "registered_on" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_admin" BOOL NOT NULL  DEFAULT False,
    "is_staff" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
