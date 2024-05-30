import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

DEV_DB_URL = os.getenv("DEV_DB_URL")
engine = create_engine(DEV_DB_URL)
sessionlocal = sessionmaker(bind=engine, autoflush=True, autocommit=False)

BaseModel = declarative_base()


def get_db_session():
    db = sessionlocal()
    try:
        return db
    finally:
        db.close()
