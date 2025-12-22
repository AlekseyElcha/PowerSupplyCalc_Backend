from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from backend.dependencies import SessionDep
from backend.database.models import Motherboard
from backend.schemas.schemas import MotherboardCreate

router = APIRouter(prefix="/motherboards", tags=["Motherboards"])

@router.post("/")
async def create_motherboard(motherboard_data: MotherboardCreate, session: SessionDep):
    try:
        motherboard = Motherboard(**motherboard_data.model_dump())
        session.add(motherboard)
        await session.commit()
        await session.refresh(motherboard)
        return {"success": True, "data": motherboard}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating Motherboard: {str(e)}")

@router.get("/")
async def get_motherboards(session: SessionDep):
    try:
        result = await session.execute(select(Motherboard))
        motherboards = result.scalars().all()
        return {"success": True, "data": motherboards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching motherboards: {str(e)}")