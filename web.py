import asyncio
from enum import Enum
from typing import Callable

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# App setup & middlewares
app = FastAPI(
    title="Driver Service Example",
)
REQUEST_TIMEOUT = 600  # 10m


@app.middleware("http")
async def timeout_middleware(
    request: Request, call_next: Callable[[Request], Response]
):
    """
    Limits request processing time
    """
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(
            {"detail": "Request processing time exceeded limit"},
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
        )


# Schema


class AuthType(Enum):
    login = "login"
    token = "token"


class InfoResponse(BaseModel):
    name: str
    slug: str
    auth_type: AuthType


class AccountInfo(BaseModel):
    name: str
    native_id: str


class AccountsResponse(AccountInfo):
    accounts: list[AccountInfo]


async def valid_token(authorization_token: str = Header(None, min_length=1)) -> str:
    # example token verification
    if authorization_token != "super_secret_token":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid authorization"
        )
    # maybe return any common info about token instead
    return authorization_token


async def valid_login(
    authorization_login: str = Header(None, min_length=1),
    authorization_password: str = Header(None, min_length=1),
) -> tuple[str, str]:
    # example login & password verification
    if (
        authorization_login != "super_secret_login"
        or authorization_password != "super_secret_password"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid authorization"
        )
    # maybe return any common info about login instead
    return authorization_login, authorization_password


# API endpoints


@app.get("/info", response_model=InfoResponse)
async def info() -> InfoResponse:
    return InfoResponse(
        name="Driver Service Example",
        slug="driver_service_example",
        auth_type=AuthType.token,
    )


@app.post("/accounts", response_model=AccountsResponse)
async def accounts(token: str = Depends(valid_token)) -> AccountsResponse:
    return AccountsResponse(
        name="Account 1",
        native_id="acc1",
        accounts=[
            AccountInfo("Account 1", "acc1"),
            AccountInfo("Account 2", "acc2"),
            AccountInfo("Account 3", "acc3"),
        ],
    )
