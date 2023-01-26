# -*-coding:utf8-*-
import os
from fastapi import FastAPI
from fastapi.middleware import Middleware
from main.db import createDbAndTables
from main.middleware import FilterEmptyQueryParamsMiddleware


def startApi() -> FastAPI:
    api = FastAPI(
        title="Energy company case REST API",
        version=os.environ.get("VERSION", "0.1.0"),
        on_startup=[createDbAndTables],
        middleware=[Middleware(FilterEmptyQueryParamsMiddleware)]  # NOTE: see https://github.com/tiangolo/fastapi/issues/1147
    )

    from main.routers.core import router as core

    api.include_router(core)

    from main.routers.admin import router as admin

    api.include_router(admin)

    return api
