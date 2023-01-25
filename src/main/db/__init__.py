# -*-coding:utf8-*-
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from main.db.models import Base

username = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PASSWORD")
dbname = os.environ.get("POSTGRES_DB")
host = os.environ.get("POSTGRES_HOST")
port = os.environ.get("POSTGRES_PORT", 5432)
DB_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"
engine = create_engine(DB_URL, future=True)


def createDbAndTables():
    Base.metadata.create_all(engine)


def getSession():
    with Session(engine, future=True) as session:
        yield session
