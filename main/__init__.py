# -*-coding:utf8-*-
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from main.db import create_db_and_tables
from main.middleware import FilterEmptyQueryParamsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with create_db_and_tables():
        yield


def start_api() -> FastAPI:
    api = FastAPI(
        title="Energy company case REST API",
        version=os.environ.get("VERSION", "0.1.0"),
        lifespan=lifespan,
        middleware=[
            Middleware(GZipMiddleware),
            Middleware(FilterEmptyQueryParamsMiddleware),  # NOTE: see https://github.com/tiangolo/fastapi/issues/1147
            Middleware(PrometheusMiddleware),
        ],
    )

    from main.routers.core import router as core

    api.include_router(core)

    from main.routers.admin import router as admin

    api.include_router(admin)

    api.add_route("/metrics", handle_metrics)

    return api
