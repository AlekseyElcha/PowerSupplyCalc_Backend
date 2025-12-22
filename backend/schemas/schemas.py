from pydantic import BaseModel

class ComponentCreate(BaseModel):
    name: str


class CPUCreate(ComponentCreate):
    consumption: float
    pass

class GPUCreate(ComponentCreate):
    consumption: float
    pass

class RAMCreate(ComponentCreate):
    consumption: float
    pass

class PSUCreate(ComponentCreate):
    wattage: float
    pass

class StorageCreate(ComponentCreate):
    consumption: float
    type: str

class CoolingCreate(ComponentCreate):
    consumption: int

class DriveCreate(ComponentCreate):
    consumption: int

class MotherboardCreate(ComponentCreate):
    consumption: int
