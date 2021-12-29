import asyncio
import datetime
from enum import Enum
from typing import Callable

from fastapi import Body, Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# App setup & middlewares
from fake_api import AuthError, FakeExtAPI

app = FastAPI(
    title="Driver Service Example",
)
REQUEST_TIMEOUT = 600  # 10m


@app.middleware("http")
async def timeout_middleware(
    request: Request, call_next: Callable[[Request], Response]
):
    """
    Ограничение времени обработки запроса
    """
    try:
        return await asyncio.wait_for(call_next(request), timeout=REQUEST_TIMEOUT)
    except asyncio.TimeoutError:
        return JSONResponse(
            {"detail": "request processing timeout"},
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


class CredentialsResponse(BaseModel):
    name: str
    native_id: str
    accounts: list[AccountInfo]


class StatsItem(BaseModel):
    date: datetime.date
    campaign: str
    value: int


# API endpoints


async def fake_external_api(authorization_token: str = Header(...)) -> FakeExtAPI:
    return FakeExtAPI(authorization_token)


@app.get("/info", response_model=InfoResponse)
async def info():
    return InfoResponse(
        name="Driver Service Example",
        slug="driver_service_example",
        auth_type=AuthType.token,
    )


@app.post("/accounts", response_model=CredentialsResponse)
async def accounts(api: FakeExtAPI = Depends(fake_external_api)):
    try:
        data = api.get_user_info()
        # возвращаем информацию например о владельце токена и список его аккаунтов
        return CredentialsResponse(
            name=data["email"],
            native_id=data["id"],
            accounts=[
                AccountInfo(name=acc["name"], native_id=acc["id"])
                for acc in data["accounts"]
            ],
        )
    except AuthError as ex:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.post("/check")
async def check(
    native_id: str = Body(..., embed=True),
    api: FakeExtAPI = Depends(fake_external_api),
):
    try:
        api.get_account(native_id)
    except AuthError as ex:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )


@app.post("/stats", response_model=list[StatsItem])
async def stats(
    date: datetime.date = Body(..., embed=True),
    native_id: str = Body(..., embed=True),
    api: FakeExtAPI = Depends(fake_external_api),
):
    try:
        data = api.get_data(native_id, date)
        return [
            StatsItem(date=item["date"], campaign=item["name"], value=item["value"])
            for item in data
        ]
    except AuthError as ex:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex)
        )
