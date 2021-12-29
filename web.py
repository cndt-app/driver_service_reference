import asyncio
import datetime
import random
from enum import Enum
from typing import Callable

from fastapi import Body, Depends, FastAPI, Header, HTTPException
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


class StatsItem(BaseModel):
    date: datetime.date
    campaign: str
    value: int


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
async def info():
    return InfoResponse(
        name="Driver Service Example",
        slug="driver_service_example",
        auth_type=AuthType.token,
    )


@app.post("/accounts", response_model=AccountsResponse)
async def accounts(token: str = Depends(valid_token)):
    return AccountsResponse(
        name="Account 1",
        native_id="acc1",
        accounts=[
            AccountInfo("Account 1", "acc1"),
            AccountInfo("Account 2", "acc2"),
            AccountInfo("Account 3", "acc3"),
        ],
    )


@app.post("/check")
async def check(
    native_id: str = Body(..., embed=True),
    token: str = Depends(valid_token),
):
    if native_id == "acc1":
        return
    elif native_id == "acc2":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid authorization"
        )
    elif native_id == "acc3":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unknown error"
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="unexpected native_id"
    )


@app.post("/stats", response_model=list[StatsItem])
async def stats(
    date: datetime.date = Body(..., embed=True),
    native_id: str = Body(..., embed=True),
    token: str = Depends(valid_token),
):
    if native_id == "acc1":
        return [
            # explicit model return
            StatsItem(
                date=date, campaign="Campaign 1", value=random.randint(0, 100500)
            ),
            # acceptable too, will be converted with validation into model automatically
            {
                "date": date,
                "campaign": "Campaign 2",
                "value": random.randint(0, 100500),
            },
        ]
    elif native_id == "acc2":
        return []
    elif native_id == "acc3":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unknown error"
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="unexpected native_id"
    )
