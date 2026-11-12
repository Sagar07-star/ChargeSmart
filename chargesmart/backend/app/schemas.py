from typing import Literal
from pydantic import BaseModel, Field, model_validator
class Point(BaseModel):
    lat: float = Field(ge=-90,le=90)
    lon: float = Field(ge=-180,le=180)
class Plan(BaseModel):
    start: Point
    end: Point
    capacity: float = Field(default=45,gt=0,le=250)
    battery: float = Field(default=60,gt=0,le=100)
    reserve: float = Field(default=15,ge=0,lt=100)
    efficiency: float = Field(default=.16,gt=0,le=2)
    connector: str = 'CCS2'
    max_charge_kw: float = Field(default=60,gt=0,le=1000)
    mode: Literal['demo','live'] = 'demo'
    @model_validator(mode='after')
    def reserve_check(self):
        if self.reserve >= self.battery: raise ValueError('Current battery must exceed reserve')
        return self
class Recommend(BaseModel):
    location: Point
    connector: str = 'CCS2'
    capacity: float = Field(default=45,gt=0,le=250)
    battery: float = Field(default=60,gt=0,le=100)
    reserve: float = Field(default=15,ge=0,lt=100)
    efficiency: float = Field(default=.16,gt=0,le=2)
    max_charge_kw: float = Field(default=60,gt=0,le=1000)
class Wait(BaseModel):
    station_id: str
    hour: int = Field(default=12,ge=0,le=23)
    day: int = Field(default=0,ge=0,le=6)
    occupancy: float = Field(default=.5,ge=0,le=1)
class ReportIn(BaseModel):
    station_id: str
    issue: Literal['Charger not working','Charger occupied','Incorrect location','Incompatible connector information','Inaccurate charging details','Other issue']
    description: str = Field(min_length=5,max_length=2000)
