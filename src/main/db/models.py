from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.types import FLOAT, INTEGER, TIMESTAMP, VARCHAR

Base = declarative_base()


class ParkRow(Base):
    __tableschema__ = "public"
    __tablename__ = "parks"
    name = Column(VARCHAR(50), primary_key=True)
    timezone = Column(VARCHAR(50))
    energy_type = Column(VARCHAR(50))
    energy_readings = relationship("EnergyReadingRow", back_populates="park", cascade="all, delete-orphan")


class EnergyReadingRow(Base):
    __tableschema__ = "public"
    __tablename__ = "energy_readings"
    id = Column(INTEGER, primary_key=True)
    megawatts = Column(FLOAT)
    timestamp = Column(TIMESTAMP)
    park_name = Column(VARCHAR(50), ForeignKey("parks.name"))
    park = relationship("ParkRow", back_populates="energy_readings")
