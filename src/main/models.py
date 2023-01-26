from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field

from main.constraints import EnergyType, ParkName, Timezone


class EnergyReading(BaseModel):
    megawatts: float
    timestamp: datetime


class Park(BaseModel):
    name: ParkName
    timezone: Timezone
    energy_type: EnergyType
    energy_readings: List[EnergyReading] = Field(None)

    class Config:
        orm_mode = True


class StatsBase(BaseModel):
    date: date
    min: float
    max: float
    sum: float
    count: int

    class Config:
        orm_mode = True


class ParkStats(StatsBase):
    name: ParkName


class EnergyTypeStats(StatsBase):
    energy_type: EnergyType
