from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.database import engine, Base

# Импортируем модели, чтобы Base знал о всех таблицах
from app.models import user, schedule  # noqa: F401
from app.routers import auth, categories, tasks, dashboard

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def wait_for_db(retries: int = 15, delay: float = 3.0):
    """Ждём пока PostgreSQL готов — актуально в docker-compose."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Database is ready!")
            return
        except Exception as e:
            logger.warning(f"⏳ DB not ready [{attempt}/{retries}]: {e}")
            if attempt < retries:
                await asyncio.sleep(delay)
    raise RuntimeError("❌ Cannot connect to database after retries")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ All tables created / verified")
    yield
    await engine.dispose()


app = FastAPI(
    title="SaaS Dashboard API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "0.1.0"}