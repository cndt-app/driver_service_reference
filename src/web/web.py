import datetime
import zoneinfo
from decimal import Decimal
from enum import Enum

from fastapi import Body, Header, HTTPException, APIRouter, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request

from src.driver.ext_api import FakeExtAPI, AuthError
from src.driver.conduit_lib import make_result_script


templates = Jinja2Templates(directory='src/templates')
router = APIRouter()


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


@router.api_route('/connect', methods=['GET', 'POST'], response_class=HTMLResponse)
async def show_connect(
    request: Request,
    # query parameters from Conduit
    rid: str,
    origin: str,
    # data submitted by form
    brand: str = Form(''),
    login: str = Form(''),
    password: str = Form(''),
):

    # show form
    if request.method == 'GET':
        return templates.TemplateResponse('connect.html', {'request': request, 'form_data': {}, 'error': None})

    secrets = {
        'brand': brand,
        'login': login,
        'password': password,
    }
    # pseudo-validation
    if not all(secrets.values()):

        return templates.TemplateResponse(
            'connect.html',
            {'request': request, 'form_data': secrets, 'error': 'Please fill all fields'},
        )

    return templates.TemplateResponse(
        'result.html',
        {'request': request, 'result_script': make_result_script(rid=rid, origin=origin, secrets=secrets)}
    )


@router.post("/stats", response_model=list[AdStatsItem])
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
