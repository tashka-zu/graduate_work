import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tortoise.contrib.fastapi import register_tortoise

from authentication.database import seed_defaults
from authentication.errors import AppError
from authentication.routers.auth import router as auth_router
from authentication.routers.private_users import router as private_users_router
from authentication.routers.users import router as users_router

app = FastAPI(
    title="Kefir Python Junior Test",
    description="Сервис для хранения данных о пользователях",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(private_users_router)


# Initialize Tortoise via official FastAPI integration.
register_tortoise(
    app,
    db_url=os.getenv(
        "DATABASE_URL",
        "postgres://postgres:tasha1502@localhost:5432/graduate_work_db",
    ),
    modules={"models": ["authentication.models.user", "authentication.models.city"]},
    generate_schemas=True,
    add_exception_handlers=False,
)


@app.on_event("startup")
async def startup() -> None:
    await seed_defaults()


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в сервис хранения данных о пользователях!"}


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError):
    if exc.code is not None:
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


@app.exception_handler(Exception)
async def internal_error_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "что-то пошло не так, мы уже исправляем эту ошибку"},
    )