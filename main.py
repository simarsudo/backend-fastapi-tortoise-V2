from fastapi import FastAPI
from contextlib import asynccontextmanager
from tortoise.contrib.fastapi import RegisterTortoise
from models import Customer, Address
from config import TORTOISE_ORM
from typing import AsyncGenerator


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


@app.get("/")
async def get_customers():
    customer = await Customer.get(id=1)
    addresses = await customer.addresses.all()
    return addresses
