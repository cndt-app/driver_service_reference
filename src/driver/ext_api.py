import datetime
from typing import Any, Iterator
from zoneinfo import ZoneInfo


class AuthError(Exception):
    pass


class FakeExtAPI:
    """
    This is just the API/SDK example
    Real checks & responses obviously should come from API/SDK
    """

    def __init__(self, login: str, password: str):
        self._login = login
        self._password = password

    def get_data(self, account_id: str, date: datetime.date, tz: ZoneInfo) -> list[dict[str, Any]]:
        if self._login != "test login":
            raise AuthError("invalid login or password")

        if account_id == "acc_no_data":
            # all ok, login has access to the account, no data available
            return []
        elif account_id == "acc_no_access":
            # login does not have access to the account
            raise AuthError("account access denied")
        elif account_id == "acc_unknown_error":
            # something happens, unknown error
            raise Exception("unknown error")
        else:
            # all ok, login has access to the account, some data available
            return list(self._make_rows(account_id, date, 10))

    @staticmethod
    def _make_rows(account_id: str, date: datetime.date, count: int) -> Iterator[dict[str, str]]:
        for i in range(1, count + 1):

            yield {
                'date': date.isoformat(),
                'ad_account': account_id,
                'ad_account_name': f'Account {account_id}',
                'campaign': f'Campaign {i}',
                'campaign_id': f'camp_{i}',
                'adgroup': '',
                'adgroup_id': '',
                'ad': '',
                'ad_id': '',
                'country': 'US',
                'ad_network': 'Example Network',
                'spend': '100.2',
                'impressions': '10',
                'clicks': '42',
                'purchases': '12',
                'link_clicks': '2',
                'adds_to_cart': '0',
                'ad_network_installs': '0',
                'actions_lead': '0',
                'actions_pixel_lead': '0',
                'ad_network_sessions': '0',
                'all_conversions': '0',
            }
