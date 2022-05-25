import asyncio
import datetime
import zoneinfo
from decimal import Decimal
from enum import Enum
from typing import Callable

# App setup & middlewares
from fastapi import Body, FastAPI, Header, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .ext_api import AuthError, FakeExtAPI

app = FastAPI(
    title="Driver Service Example",
)
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


# API Schema


class AuthType(Enum):
    login = "login"
    token = "token"


class AdStatsItem(BaseModel):
    date: datetime.date
    ad_account: str
    ad_account_name: str
    campaign: str
    campaign_id: str
    adgroup: str
    adgroup_id: str
    ad: str
    ad_id: str
    country: str
    ad_network: str

    spend: Decimal
    impressions: int
    clicks: int
    purchases: int
    link_clicks: int
    adds_to_cart: int
    ad_network_installs: int
    actions_lead: int
    actions_pixel_lead: int
    ad_network_sessions: int
    all_conversions: int


# API endpoints


@app.post("/stats", response_model=list[AdStatsItem])
async def stats(
    date: datetime.date = Body(..., embed=True, example='2022-01-01'),
    tz: str = Body(..., embed=True, example='Europe/Monaco'),
    native_id: str = Body(..., embed=True, example='account'),
    authorization_login: str = Header(..., example='test login'),
    authorization_password: str = Header(..., example='test password'),
):
    try:
        tz = zoneinfo.ZoneInfo(tz)
    except zoneinfo.ZoneInfoNotFoundError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'invalid timezone: {tz}')

    api = FakeExtAPI(authorization_login, authorization_password)

    try:
        return [AdStatsItem(**row) for row in api.get_data(native_id, date, tz)]
    except AuthError as ex:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))
