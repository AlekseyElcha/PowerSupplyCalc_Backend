from sqlalchemy.orm import Mapped, mapped_column
from backend.database.database import Base

class ComponentBase(Base):
    __abstract__ = True
    name: Mapped[str] = mapped_column(primary_key=True)

class CPU(ComponentBase):
    __tablename__ = "cpus"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[str] = mapped_column()

class GPU(ComponentBase):
    __tablename__ = "gpus"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[str] = mapped_column()

class PSU(ComponentBase):
    __tablename__ = "psus"
    __table_args__ = {"extend_existing": True}
    wattage: Mapped[str] = mapped_column()

class RAM(ComponentBase):
    __tablename__ = "ram"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[str] = mapped_column()

class Storage(ComponentBase):
    __tablename__ = "storages"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[str] = mapped_column()

class Cooling(ComponentBase):
    __tablename__ = "cooling"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[int] = mapped_column()

class Drive(ComponentBase):
    __tablename__ = "drives"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[int] = mapped_column()

class Motherboard(ComponentBase):
    __tablename__ = "motherboards"
    __table_args__ = {"extend_existing": True}
    consumption: Mapped[int] = mapped_column()
