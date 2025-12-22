import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from routers import cpus, gpus, system, ram, storages, cooling, psus, drives, motherboards
from database.database import engine, Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных инициализирована")

    yield
    logger.info("Завершение работы приложения...")

app = FastAPI(
    title="PC Components API",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(system.router)
app.include_router(cpus.router)
app.include_router(gpus.router)
app.include_router(psus.router)
app.include_router(ram.router)
app.include_router(storages.router)
app.include_router(cooling.router)
app.include_router(drives.router)
app.include_router(motherboards.router)

@app.get("/")
async def root():
    return {
        "message": "PC Components API",
        "docs": "/docs",
        "redoc": "/redoc"
    }
