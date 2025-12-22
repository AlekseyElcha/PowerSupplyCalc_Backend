from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from backend.dependencies import SessionDep
from backend.database.models import Drive
from backend.schemas.schemas import DriveCreate

router = APIRouter(prefix="/drives", tags=["Drives"])

@router.post("/")
async def create_drive(drive_data: DriveCreate, session: SessionDep):
    try:
        drive = Drive(**drive_data.model_dump())
        session.add(drive)
        await session.commit()
        await session.refresh(drive)
        return {"success": True, "data": drive}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating Drive: {str(e)}")

@router.get("/")
async def get_drives(session: SessionDep):
    try:
        result = await session.execute(select(Drive))
        drives = result.scalars().all()
        return {"success": True, "data": drives}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching drives: {str(e)}")