from fastapi import FastAPI
from authentication.database import init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Сервис для хранения данных о пользователях",
    description="API для управления пользователями и их данными",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в сервис хранения данных о пользователях!"}