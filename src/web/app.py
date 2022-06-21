import asyncio
from typing import Callable

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from . import web

app = FastAPI(
    title="Driver Service Example",
)
app.include_router(web.router)

REQUEST_TIMEOUT = 600  # 10m


@app.middleware("http")
async def timeout_middleware(request: Request, call_next: Callable[[Request], Response]):
    """
    Limits request processing time and returns HTTP 408 when exceeds
    """
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(
            {"detail": "request processing timeout"},
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )
