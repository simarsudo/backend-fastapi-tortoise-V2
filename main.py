import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import RegisterTortoise
from config import TORTOISE_ORM
from typing import AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routes import account_routes, admin_route, actions_routes, products_routes

load_dotenv()
DEV = os.getenv("DEV")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # app startup
    async with RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        # db connected
        yield
        # app teardown
    # db connections closed


app = FastAPI(title="Tortoise ORM FastAPI example", lifespan=lifespan)


if DEV:
    origins = [
        "http://localhost:3000",
    ]
    # Todo Add check if running in dev or prod and do the same in frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(account_routes.router, prefix="/account", tags=["Account"])
app.include_router(admin_route.router, prefix="/admin", tags=["Admin"])
app.include_router(actions_routes.router, prefix="/actions", tags=["Actions"])
app.include_router(products_routes.router, prefix="/products", tags=["Product"])
