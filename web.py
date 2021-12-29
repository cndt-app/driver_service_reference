import asyncio
import datetime
import random
from enum import Enum
from typing import Callable

from fastapi import Body, FastAPI, Header, HTTPException
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


@app.get("/info", response_model=InfoResponse)
async def info():
    return InfoResponse(
        name="Driver Service Example",
        slug="driver_service_example",
        auth_type=AuthType.token,
    )


@app.post("/accounts", response_model=CredentialsResponse)
async def accounts(authorization_token: str = Header(...)):
    # само собой, проверка должна быть на стороне внешнего API и почти всегда при запросе данных,
    # тут пример результатов обработки ответа с хардкодом токена
    if authorization_token != "super_secret_token":
        # пример обработки невалидного токена, например устаревший
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid token"
        )

    # возвращаем информацию например о владельце токена и список его аккаунтов
    return CredentialsResponse(
        name="some-api-user@example.com",
        native_id="user123321",
        accounts=[
            AccountInfo(name="Account 1", native_id="acc1"),
            AccountInfo(name="Account 2", native_id="acc2"),
            AccountInfo(name="Account 3", native_id="acc3"),
        ],
    )


@app.post("/check")
async def check(
    native_id: str = Body(..., embed=True),
    authorization_token: str = Header(...),
):
    # само собой, проверка должна быть на стороне внешнего API и почти всегда при запросе данных,
    # тут пример результатов обработки ответа с хардкодом токена
    if authorization_token != "super_secret_token":
        # пример обработки невалидного токена, например устаревший
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid token"
        )

    if native_id == "acc1":
        # всё ок, по токену есть доступ к аккаунту
        return
    elif native_id == "acc3":
        # пример неизвестной ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unknown error"
        )

    # пример отсутствия доступа к аккаунту по токену
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account access denied")


@app.post("/stats", response_model=list[StatsItem])
async def stats(
    date: datetime.date = Body(..., embed=True),
    native_id: str = Body(..., embed=True),
    authorization_token: str = Header(...),
):
    # само собой, проверка должна быть на стороне внешнего API и почти всегда при запросе данных,
    # тут пример результатов обработки ответа с хардкодом токена
    if authorization_token != "super_secret_token":
        # пример обработки невалидного токена, например устаревшего
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid token"
        )

    if native_id == "acc1":
        # всё ок, по токену есть доступ к аккаунту и есть данные
        return [
            # явная передача модели
            StatsItem(
                date=date, campaign="Campaign 1", value=random.randint(0, 100500)
            ),
            # передача данных тоже допустима, fastapi конвертирует и валидирует автоматически
            {
                "date": date,
                "campaign": "Campaign 2",
                "value": random.randint(0, 100500),
            },
        ]
    elif native_id == "acc2":
        # тоже всё ок, по токену есть доступ к аккаунту, но данных нет
        return []
    elif native_id == "acc3":
        # пример неизвестной ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="unknown error"
        )

    # пример отсутствия доступа к аккаунту по токену
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account access denied")
