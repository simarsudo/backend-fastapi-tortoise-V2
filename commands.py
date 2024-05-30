import typer
import sqlalchemy
import os
import subprocess
import docker
from faker import Faker
from tortoise import Tortoise, run_async
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()


app = typer.Typer()
fake = Faker()

USERNAME = os.getenv("USER_NAME")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
FULLNAME = os.getenv("FULL_NAME")
DEV_DB_URL = os.getenv("DEV_DB_URL")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url=DEV_DB_URL, modules={"models": ["models.user_model", "aerich.models"]}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


@app.command()
def generate_models():
    run_async(init())


if __name__ == "__main__":
    app()
