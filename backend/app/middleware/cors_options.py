"""Ensure OPTIONS preflight for auth routes always returns 200 with CORS headers."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class AuthCorsOptionsMiddleware(BaseHTTPMiddleware):
    """
    Handles OPTIONS for /api/v1/auth/* explicitly so preflight never returns 400.
    Add before CORSMiddleware (i.e. add_middleware after CORS) so we run first.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method != "OPTIONS":
            return await call_next(request)
        path = request.scope.get("path", "")
        if not path.startswith("/api/v1/auth/"):
            return await call_next(request)

        origin = request.headers.get("origin", "")
        acrh = request.headers.get("access-control-request-headers", "content-type, authorization")
        allowed = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else []
        allow_origin = origin if origin in allowed else ""

        headers = {
            "access-control-allow-methods": "GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "access-control-allow-headers": acrh,
            "access-control-allow-credentials": "true",
            "access-control-max-age": "86400",
        }
        if allow_origin:
            headers["access-control-allow-origin"] = allow_origin
        return Response(status_code=200, headers=headers)
