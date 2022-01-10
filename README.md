# Driver Service Reference

## Глоссарий

* **Partner API** - внешнее API представляющее статистические данные, с которым работает Драйвер.
* **Driver** - сервис, который реализует стандартизированный API для интеграции с Partner API.
* **Авторизационные данные** - данные (например логин и пароль), необходимые для авторизации запросов в Partner API.
* **Аккаунт** - сущность в Partner API позволяющая получить доступ к статистическим данным по Авторизационным данным.
  Некоторые Partner API предполагают наличие многих Аккаунтов (пример Facebook - Ad Accounts), некоторые не предполагают
  их наличие совсем (пример Shopify - там всегда один магазин), а в некоторых Аккаунтом может выступать сгенерированная
  сущность (например для запроса аналитической статистики нужно передать сайт+конкретный отчет - в таком случае Драйвер
  может генерировать Аккаунты из набора сайт+отчет).

## Driver’s API

Драйвер должен реализовать 4 метода:

* **/info**
* **/accounts**
* **/check**
* **/stats**

### Авторизация запросов

Методы, за исключением **/info** должны ожидать передачи авторизационных данных.

Авторизационные данные будут передаваться в хедерах при вызове API драйвера, для дальнейшей авторизации в Partner API.

***Строжайшим образом запрещается логировать, сохранять, и передавать куда-либо Авторизационные данные.***

При реализации драйвера, нужно выбрать один из способов авторизации в Partner API:

* **Login & password**
* **Token**

**Login & Password** - в случае этого типа авторизации Авторизационные данные будут передаваться 2 хэдерами:

* Authorization-Login
* Authorization-Password

**Token** - в случае этого типа авторизации Авторизационные данные будут передаваться одним хэдером:

* Authorization-Token

### API /info

Метод возвращает базовую информацию о драйвере и поддерживаемом методе передачи Авторизационных данных.

```
GET /info
Request body - empty
Response - JSON
{
  "name": str,  # Название Драйвера. Не должно меняться  
  "slug": str,  # [a-z_] Техническое название Драйвера. Не должно меняться. 
  "auth_type": str # ENUM [ "login", "token" ] 
}
```

### API /accounts

Метод возвращает базовую информацию из Partner API идентифицирующую авторизационные данные, а также доступные Аккаунты.

```
POST /accounts
Auth Required
Request body - empty
Response - JSON
{
  "name": "John Doe",
  "native_id": "a329312c9cd",
  
  "accounts": [
    {
      "name": "Sneakers Shop",  
      "native_id": "b3933793c1cd",  
    },
    {
      "name": "Auto Parts Shop",  
      "native_id": "120aee9af4a0d",  
    }
  ]
}
```

### API /check

Выполняет проверку доступа к аккаунту

```
POST /check
Auth Required
Request body - JSON
{
  "native_id": str # account native id 
}

Response - HTTP OK or HTTP ERROR
```

### API /stats

Возвращает статистику в согласованном формате с набором определенных полей итд

```
POST /stats
Auth Required
Request body - JSON
{
  "date": str, # iso date string
  "native_id": str, # account native id 
}
Response - JSON
[
  {...},
  {...},
]
```

### Ожидаемые HTTP-статусы

* **200** - OK - запрос прошёл успешно
* **400** - Bad Request - ошибка запроса в Partner API (такое может быть например если сервис требует обновления SDK)
* **403** - Invalid Authorization - Partner API ответил, что данные авторизации некорректные (например протухший токен)
* **408** - Request Timeout - запрос не уложился в таймаут
* **422** - Unprocessable Entity - нарушение API драйвера (например некорректный запрос)
* **429** - Rate Limit - сработали сервисные ограничения Partner API (например частота запросов)
* **500** - Unhandled Service Crash - что-то пошло не так и сервис не может обработать эту ошибку

Все ошибки должны возвращать в Body подробности ошибки.

### Общие типы данных

Во многих драйверах типы возвращаемых данных пересекаются, список общих типов и форматов, к которым данные нужно
привести:

* **Коды стран** - всегда двухбуквенный код **ISO 3166-1** (Россия - `RU`, США - `US`)
* **Все нецелочисленные данные** - всегда строкой как Decimal для избежания потери точности (3,14159 - `"3,14159"`,
  123456 - `123456`)
* **Валюты** - всегда трёхбуквенный код **ISO 4217**, по умолчанию в долларах США - `USD`. 
    * **Если Partner API работает не с USD - нужно отдельно согласовывать решение.**
* **Дата и время** - формат **ISO 8601** `YYYY-MM-DDThh:mm:ssZ` (`2021-12-30T14:49:28Z`)
    * **Только дата** - формат `YYYY-MM-DD` (`2021-12-30`)
    * **Только время** - формат `hh:mm:ss` (`14:49:28`)
    * **Тайм-зона всегда должна быть в UTC. Если Partner API работает с другой - нужно согласовать решение.**

### Таймауты

Сервис должен отдавать ответ за 10 минут. Если не успевает - возвращать **408 Request Timeout**.

### Рейт-лимиты

Сервис должен учитывать наличие рейт-лимитов и ограничений Partner API. 
Например, реализовывать самостоятельно ограничения вызовов к Partner API и корректно возвращать **429 Rate Limit**.

### Пагинация

Сервис должен возвращать результаты с учётом пагинации - выкачивать все страницы и отдавать данные уже без пагинации.
