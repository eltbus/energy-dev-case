from urllib.parse import parse_qsl, urlencode

from starlette.types import ASGIApp, Receive, Scope, Send


class FilterEmptyQueryParamsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope and scope.get("query_string"):
            filtered_query_params = parse_qsl(
                qs=scope["query_string"].decode("latin-1"),
                keep_blank_values=False,
            )
            scope["query_string"] = urlencode(filtered_query_params).encode("latin-1")
        await self.app(scope, receive, send)
