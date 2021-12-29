import datetime
from typing import Any


class AuthError(Exception):
    pass


class FakeExtAPI:
    """
    This is just the API/SDK example
    Real checks & responses obviously should become from API/SDK
    """

    def __init__(self, token: str):
        self._token = token

    def get_accounts(self) -> list[dict[str, Any]]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        return [
            {"id": "acc1", "name": "Account 1"},
            {"id": "acc2", "name": "Account 2"},
            {"id": "acc3", "name": "Account 3"},
        ]

    def get_user_info(self) -> dict[str, Any]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        return {"id": "user123", "name": "Some API User"}

    def get_account(self, account_id: str) -> dict[str, Any]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        if account_id == "acc1":
            # all ok, token has access to the account
            return {"id": account_id}
        elif account_id == "acc3":
            # something happens, unknown error
            raise Exception("unexpected error")

        # token does not have access to the account
        raise AuthError("account access denied")

    def get_data(self, account_id: str, date: datetime.date) -> list[dict[str, Any]]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        if account_id == "acc1":
            # all ok, token has access to the account, some data available
            return [
                {
                    "date": date,
                    "name": "Campaign 1",
                    "country": "US",
                    "account_id": "acc1",
                    "clicks": 12,
                    "installs": 2,
                },
                {
                    "date": date,
                    "name": "Campaign 2",
                    "country": "US",
                    "account_id": "acc1",
                    "clicks": 5,
                    "installs": 1,
                },
            ]
        elif account_id == "acc2":
            # all ok, token has access to the account, no data available
            return []
        elif account_id == "acc3":
            # something happens, unknown error
            raise Exception("unknown error")

        # token does not have access to the account
        raise AuthError("account access denied")
