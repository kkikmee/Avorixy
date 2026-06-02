from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import engine, Base

# Импортируем модели, чтобы Base знал о всех таблицах
from app.models import user, schedule  # noqa: F401
from app.routers import auth, categories, tasks, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте (для продакшена используй Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="SaaS Dashboard API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "0.1.0"}