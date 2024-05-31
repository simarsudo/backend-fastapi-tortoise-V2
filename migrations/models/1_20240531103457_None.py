from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "customer" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50) NOT NULL,
    "phone_no" VARCHAR(10) NOT NULL,
    "is_disabled" BOOL NOT NULL  DEFAULT False,
    "password_hash" VARCHAR(150) NOT NULL,
    "token" VARCHAR(200),
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
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50) NOT NULL,
    "phone_no" VARCHAR(10) NOT NULL,
    "is_disabled" BOOL NOT NULL  DEFAULT False,
    "password_hash" VARCHAR(150) NOT NULL,
    "token" VARCHAR(200),
    "registered_on" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_admin" BOOL NOT NULL  DEFAULT False,
    "is_staff" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "order_id" UUID NOT NULL,
    "delivery_address" JSONB NOT NULL,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "payment_details" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "card_number" VARCHAR(16) NOT NULL,
    "card_holder_name" VARCHAR(50) NOT NULL,
    "month" VARCHAR(2) NOT NULL,
    "year" VARCHAR(4) NOT NULL,
    "cvv" VARCHAR(3) NOT NULL,
    "billing_address" JSONB NOT NULL,
    "order_id" INT NOT NULL UNIQUE REFERENCES "orders" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "products" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "slug" VARCHAR(100) NOT NULL,
    "price" INT NOT NULL,
    "description" TEXT NOT NULL,
    "type" VARCHAR(20) NOT NULL
);
COMMENT ON COLUMN "products"."type" IS 'SHIRT: Shirt\nPANTS: Pants\nJOGGERS: Joggers';
CREATE TABLE IF NOT EXISTS "images" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "path" VARCHAR(100) NOT NULL,
    "product_id" INT NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_images_path_48926e" ON "images" ("path");
CREATE TABLE IF NOT EXISTS "sizes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "size" VARCHAR(5) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "cart" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "qty" INT NOT NULL,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE,
    "product_id_id" INT NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    "size_id" INT NOT NULL REFERENCES "sizes" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "inventory" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "quantity" INT NOT NULL,
    "product_id" INT NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    "size_id" INT NOT NULL REFERENCES "sizes" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "wishlist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "customer_id" INT NOT NULL REFERENCES "customer" ("id") ON DELETE CASCADE,
    "product_id" INT NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_wishlist_product_1d537a" UNIQUE ("product_id", "customer_id")
);
CREATE TABLE IF NOT EXISTS "orders_products" (
    "orders_id" INT NOT NULL REFERENCES "orders" ("id") ON DELETE CASCADE,
    "products_id" INT NOT NULL REFERENCES "products" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_orders_prod_orders__a583d8" ON "orders_products" ("orders_id", "products_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
