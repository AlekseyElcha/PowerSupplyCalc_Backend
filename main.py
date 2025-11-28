from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

engine = create_async_engine('sqlite+aiosqlite:///components.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass

@app.post("/setup_database")
async def setup_database():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        return {"success": True, "message": "database created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database setup error: {str(e)}")

class ComponentBase(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    consumption: Mapped[str] = mapped_column()

class CPU(ComponentBase):
    __tablename__ = "cpus"


class GPU(ComponentBase):
    __tablename__ = "gpus"


class RAM(ComponentBase):
    __tablename__ = "ram"

    memory_type: Mapped[str] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    speed: Mapped[int] = mapped_column()
    latency: Mapped[str] = mapped_column()

class Storage(ComponentBase):
    __tablename__ = "storages"


class PSU(ComponentBase):
    __tablename__ = "psus"


class Cooling(ComponentBase):
    __tablename__ = "cooling"

    size: Mapped[str] = mapped_column()
    has_led: Mapped[bool] = mapped_column(default=False)

class CPUCreate(BaseModel):
    name: str
    consumption: float

class GPUCreate(BaseModel):
    name: str
    consumption: float

class RAMCreate(BaseModel):
    name: str
    consumption: float
    memory_type: str
    capacity: int
    speed: int
    # ???

class PSUCreate(BaseModel):
    name: str
    consumption: float

class StorageCreate(BaseModel):
    name: str
    type: str
    consumption: float
    # ???

class CoolingCreate(BaseModel):
    name: str
    consumption: float
    # ???

'''
@app.post("/cpus/")
async def create_cpu(cpu_data: CPUCreate, session: SessionDep):
    try:
        cpu = CPU(**cpu_data.model_dump())
        session.add(cpu)
        await session.commit()
        await session.refresh(cpu)
        return {"success": True, "data": cpu}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating CPU: {str(e)}")

@app.post("/gpus/")
async def create_gpu(gpu_data: GPUCreate, session: SessionDep):
    try:
        gpu = GPU(**gpu_data.model_dump())
        session.add(gpu)
        await session.commit()
        await session.refresh(gpu)
        return {"success": True, "data": gpu}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating GPU: {str(e)}")
'''

@app.get("/cpus/")
async def get_cpus(session: SessionDep):
    try:
        result = await session.execute(select(CPU))
        cpus = result.scalars().all()
        return {"success": True, "data": cpus}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CPUs: {str(e)}")

@app.get("/gpus/")
async def get_gpus(session: SessionDep):
    try:
        result = await session.execute(select(GPU))
        gpus = result.scalars().all()
        return {"success": True, "data": gpus}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching GPUs: {str(e)}")

@app.get("/ram/")
async def get_ram(session: SessionDep):
    try:
        result = await session.execute(select(RAM))
        ram = result.scalars().all()
        return {"success": True, "data": ram}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RAM: {str(e)}")

@app.get("/storages/")
async def get_storages(session: SessionDep):
    try:
        result = await session.execute(select(Storage))
        storages = result.scalars().all()
        return {"success": True, "data": storages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching storages: {str(e)}")

@app.get("/cooling/")
async def get_colling(session: SessionDep):
    try:
        result = await session.execute(select(Cooling))
        cooling = result.scalars().all()
        return {"success": True, "data": cooling}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Coolings: {str(e)}")

@app.get("/cpus/{cpu_name}")
async def get_cooling(cpu_name: str, session: SessionDep):
    try:
        result = await session.execute(
            select(CPU).where(CPU.name.ilike(f"%{cpu_name}%"))
        )
        cpus = result.scalars().all()
        if not cpus:
            raise HTTPException(status_code=404, detail="CPUs not found")

        return {"success": True, "data": cpus}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching CPUs: {str(e)}")

@app.get("/gpus/{gpu_name}")
async def get_gpu(gpu_name: str, session: SessionDep):
    try:
        result = await session.execute(
            select(GPU).where(GPU.name.ilike(f"%{gpu_name}%"))
        )
        gpus = result.scalars().all()
        if not gpus:
            raise HTTPException(status_code=404, detail="GPUs not found")

        return {"success": True, "data": gpus}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching GPUs: {str(e)}")

@app.get("/psus/{psus_name}")
async def get_psus(psus_name: str, session: SessionDep):
    try:
        result = await session.execute(
            select(PSU).where(PSU.name.ilike(f"%{psus_name}%"))
        )
        psus = result.scalars().all()
        if not psus:
            raise HTTPException(status_code=404, detail="PSUs not found")

        return {"success": True, "data": psus}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching PSUSs: {str(e)}")

@app.get("/ram/{ram_name}")
async def get_ram(ram_name: str, session: SessionDep):
    try:
        result = await session.execute(
            select(RAM).where(RAM.name.ilike(f"%{ram_name}%"))
        )
        ram = result.scalars().all()
        if not ram:
            raise HTTPException(status_code=404, detail="RAM not found")

        return {"success": True, "data": ram}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RAM: {str(e)}")

@app.get("/storages/{storage_type}{number}")
async def get_storages(storage_type: str, number: int, session: SessionDep):
    try:
        result = await session.execute(
            select(Storage).where(Storage.name.ilike(f"%{storage_type}%"))
        )
        storages = result.scalars().all()
        if not storages:
            raise HTTPException(status_code=404, detail="Storages not found")

        return {"success": True, "data": storages}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Storages: {str(e)}")

@app.get("/cooling/{cooling_name}")
async def get_cooling(cooling_name: str, session: SessionDep):
    try:
        result = await session.execute(
            select(Cooling).where(CPU.name.ilike(f"%{cooling_name}%"))
        )
        cooling_name = result.scalars().all()
        if not cooling_name:
            raise HTTPException(status_code=404, detail="Cooling not found")

        return {"success": True, "data": cooling_name}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cooling: {str(e)}")

@app.get('/storages/{type}/{number}')
async def get_storage(type: str, number: int, session: SessionDep):
    try:
        result = await session.execute(
            select(Storage).where(Storage.name.ilike(f"%{type}%"))
        )
        ram = result.scalars().all()
        if not ram:
            raise HTTPException(status_code=404, detail="Storage not found")

        return {"success": True, "data": ram}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching RAM: {str(e)}")


@app.get("/health")
async def health_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}


@app.get("/test_connection")
async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(select(1))
        return {"status": "success", "message": "Database connection successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
