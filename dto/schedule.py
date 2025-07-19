from datetime import timedelta, datetime
from typing import List, Optional
from datetime import time as dt_time

from pydantic import BaseModel

from model.schedule import Weekday


class ScheduleExclusionIn(BaseModel):
    datetime: datetime


class ScheduleExclusionOut(BaseModel):
    datetime: datetime

    class Config:
        from_attributes = True


class ScheduleTimeModificationIn(BaseModel):
    datetime: datetime


class ScheduleTimeModificationOut(BaseModel):
    datetime: datetime

    class Config:
        from_attributes = True


class ScheduleTimeUpdateIn(BaseModel):
    time: dt_time
    datetime: datetime


class ScheduleDayOut(BaseModel):
    day: Weekday

    class Config:
        from_attributes = True


class ScheduleCreateIn(BaseModel):
    time: dt_time
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    days: List[Weekday]


class ScheduleReplaceIn(BaseModel):
    time: Optional[dt_time] = None
    days: Optional[List[Weekday]] = None


class ScheduleOut(BaseModel):
    id: int
    time: dt_time
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    days: List[ScheduleDayOut]
    exclusions: List[ScheduleExclusionOut]
    time_modifications: List[ScheduleTimeModificationOut]

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj) -> "ScheduleOut":
        time_value = obj.time

        if isinstance(time_value, timedelta):
            total_seconds = int(time_value.total_seconds())
            hours = (total_seconds // 3600) % 24
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            parsed_time = dt_time(hour=hours, minute=minutes, second=seconds)
        else:
            parsed_time = time_value

        return cls(
            id=obj.id,
            time=parsed_time,
            start_datetime=obj.start_datetime,
            end_datetime=obj.end_datetime,
            days=[ScheduleDayOut.model_validate(d) for d in obj.days],
            exclusions=[ScheduleExclusionOut.model_validate(e) for e in obj.exclusions],
            time_modifications=[
                ScheduleTimeModificationOut.model_validate(e)
                for e in obj.time_modifications
            ],
        )
