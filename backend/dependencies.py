from typing import Annotated
from fastapi import Depends
from database.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

SessionDep = Annotated[AsyncSession, Depends(get_session)]
