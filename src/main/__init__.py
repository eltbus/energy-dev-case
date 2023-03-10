# -*-coding:utf8-*-
import os

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.gzip import GZipMiddleware

from main.db import create_db_and_tables
from main.middleware import FilterEmptyQueryParamsMiddleware


def start_api() -> FastAPI:
    api = FastAPI(
        title="Energy company case REST API",
        version=os.environ.get("VERSION", "0.1.0"),
        on_startup=[create_db_and_tables],
        middleware=[
            Middleware(GZipMiddleware),
            Middleware(FilterEmptyQueryParamsMiddleware),
        ],  # NOTE: see https://github.com/tiangolo/fastapi/issues/1147
    )

    from main.routers.core import router as core

    api.include_router(core)

    from main.routers.admin import router as admin

    api.include_router(admin)

    return api
