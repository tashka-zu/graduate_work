# Graduate Work - User Data Service (FastAPI + Tortoise ORM)

Сервис хранения данных о пользователях по предоставленной OpenAPI-спецификации.

## Требования

* Python 3.11+
* PostgreSQL (для production). В тестах используется SQLite.

## Локальный запуск

1. Установите зависимости:
   * `pip install -r requirements.txt`
2. Укажите переменные окружения:
   * `DATABASE_URL` (пример для Postgres): `postgres://user:pass@localhost:5432/graduate_work_db`
   * `JWT_SECRET` (секрет для подписи JWT в cookie)
   * `COOKIE_SECURE` (`true/false`, по умолчанию `false`)

3. Запустите сервер:
   * `uvicorn main:app --reload --port 8000`

Открыть Swagger/OpenAPI UI:
* `http://localhost:8000/docs`

## Автосидирование пользователей (удобно для проверки)

При старте (после инициализации Tortoise) сервис может создать тестовых пользователей, если заданы параметры:

* `DEFAULT_ADMIN_EMAIL`, `DEFAULT_ADMIN_PASSWORD`
* `DEFAULT_SIMPLE_EMAIL`, `DEFAULT_SIMPLE_PASSWORD`
* `DEFAULT_CITY_ID` (по умолчанию `1`)
* `DEFAULT_CITY_NAME` (по умолчанию `Unknown`)

Например:
* `DEFAULT_ADMIN_EMAIL=admin@test.com`
* `DEFAULT_ADMIN_PASSWORD=adminpass`

Тогда вы сможете войти в систему через:
* `POST /login` с `{"login":"admin@test.com","password":"adminpass"}`

## Проверка API вручную

Пример (Swagger проще, но можно и через curl):

1. Логин (в ответ сервер установит cookie):
   * `curl -i -s -c cookies.txt -X POST http://localhost:8000/login -H "Content-Type: application/json" -d "{\"login\":\"admin@test.com\",\"password\":\"adminpass\"}"`
2. Получить текущего пользователя:
   * `curl -s -b cookies.txt http://localhost:8000/users/current`
3. Вызовы администратора:
   * `curl -s -b cookies.txt "http://localhost:8000/private/users?page=1&size=10"`

## Запуск в Docker

1. `docker compose up --build`
2. Swagger:
   * `http://localhost:8000/docs`

## Тесты и покрытие

Запуск тестов:
* `pytest`

Порог покрытия: минимум `75%`.
