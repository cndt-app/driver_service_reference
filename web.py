import asyncio
import datetime
from enum import Enum
from typing import Callable

from fastapi import Body, FastAPI, Header, HTTPException
from pydantic import BaseModel, BaseSettings, Field
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# App setup & middlewares
from ext_api import AuthError, FakeExtAPI

app = FastAPI(
    title="Driver Service Example",
)
REQUEST_TIMEOUT = 600  # 10m


class Settings(BaseSettings):
    driver_name: str = Field("driver_name", env='DRIVER_NAME')
    driver_slug: str = Field("driver_slug", env='DRIVER_SLUG')
    driver_auth: list = Field(["login", "token"], env='DRIVER_AUTH')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()


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


# Schema


class AuthType(Enum):
    login = "login"
    token = "token"


class InfoResponse(BaseModel):
    name: str
    slug: str
    auth_type: list[AuthType]


class AccountInfo(BaseModel):
    name: str
    native_id: str


class CredentialsResponse(BaseModel):
    name: str
    native_id: str
    accounts: list[AccountInfo]


class AccountsResponse(BaseModel):
    accounts: list[AccountInfo]


class StatsItem(BaseModel):
    date: datetime.date
    campaign: str
    country: str
    ad_account_id: str
    clicks: int
    installs: int


# API endpoints


@app.get("/info", response_model=InfoResponse)
async def info():
    return InfoResponse(
        name=settings.driver_name,
        slug=settings.driver_slug,
        auth_type=settings.driver_auth,
    )

    @app.post("/accounts", response_model=list[AccountInfo])
    async def accounts(authorization_token: str = Header(...)):
        try:
            api = FakeExtAPI(authorization_token)
            # возвращаем список его аккаунтов
            return [AccountInfo(name=acc["name"], native_id=acc["id"]) for acc in api.get_accounts()]
        except AuthError as ex:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    @app.post("/credentials", response_model=CredentialsResponse)
    async def accounts(authorization_token: str = Header(...)):
        try:
            api = FakeExtAPI(authorization_token)
            user_data = api.get_user_info()
            # возвращаем информацию например о владельце токена
            return CredentialsResponse(
                name=user_data["name"],
                native_id=user_data["id"],
            )
        except AuthError as ex:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    @app.post("/check")
    async def check(
            native_id: str = Body(..., embed=True),
            authorization_token: str = Header(...),
    ):
        try:
            FakeExtAPI(authorization_token).get_account(native_id)
        except AuthError as ex:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))

    @app.post("/stats", response_model=list[StatsItem])
    async def stats(
            date: datetime.date = Body(..., embed=True),
            native_id: str = Body(..., embed=True),
            authorization_token: str = Header(...),
    ):
        try:
            return [
                StatsItem(
                    date=item["date"],
                    campaign=item["name"],
                    country=item["country"],
                    ad_account_id=item["account_id"],
                    clicks=item["clicks"],
                    installs=item["installs"],
                )
                for item in FakeExtAPI(authorization_token).get_data(native_id, date)
            ]
        except AuthError as ex:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
        except Exception as ex:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
