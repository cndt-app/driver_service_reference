import datetime
import random
from typing import Any


class AuthError(Exception):
    pass


class FakeExtAPI:
    def __init__(self, token: str):
        self._token = token

    def get_user_info(self) -> dict[str, Any]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        return {
            "id": "user123",
            "email": "some-api-user@example.com",
            "accounts": [
                {"id": "acc1", "name": "Account 1"},
                {"id": "acc2", "name": "Account 2"},
                {"id": "acc3", "name": "Account 3"},
            ],
        }

    def get_account(self, account_id: str) -> dict[str, Any]:
        if self._token != "super_secret_token":
            raise AuthError("invalid token")

        if account_id == "acc1":
            # всё ок, по токену есть доступ к аккаунту
            return {"id": account_id}
        elif account_id == "acc3":
            # пример неизвестной ошибки
            raise Exception("unexpected error")

        # пример отсутствия доступа к аккаунту по токену
        raise AuthError("account access denied")

    def get_data(self, account_id: str, date: datetime.date) -> list[dict[str, Any]]:
        if account_id == "acc1":
            # всё ок, по токену есть доступ к аккаунту и есть данные
            return [
                {
                    "date": date,
                    "name": "Campaign 1",
                    "value": random.randint(0, 100500),
                },
                {
                    "date": date,
                    "name": "Campaign 2",
                    "value": random.randint(0, 100500),
                },
            ]
        elif account_id == "acc2":
            # тоже всё ок, по токену есть доступ к аккаунту, но данных нет
            return []
        elif account_id == "acc3":
            # пример неизвестной ошибки
            raise Exception("unknown error")

        # пример отсутствия доступа к аккаунту по токену
        raise AuthError("account access denied")
