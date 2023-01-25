# -*-coding:utf8-*-
import os

from fastapi import FastAPI

from main.db import createDbAndTables


def startApi() -> FastAPI:
    api = FastAPI(
        title="Energy company case REST API",
        version=os.environ.get("VERSION", "0.1.0"),
        on_startup=[createDbAndTables],
    )

    from main.routers.core import router as core

    api.include_router(core)

    from main.routers.admin import router as admin

    api.include_router(admin)

    return api
