from datetime import date, datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from main.constraints import EnergyType, ParkName, Timezone


class EnergyReading(BaseModel):
    megawatts: float
    timestamp: datetime


class Park(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: ParkName
    timezone: Timezone
    energy_type: EnergyType
    energy_readings: List[EnergyReading] = Field(None)


class StatsBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: date
    min: float
    max: float
    sum: float
    count: int


class ParkStats(StatsBase):
    name: ParkName


class EnergyTypeStats(StatsBase):
    energy_type: EnergyType
