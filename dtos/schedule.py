from datetime import date, time, timedelta, datetime
from typing import List, Optional

from pydantic import BaseModel

from models.schedule import Weekday


class ScheduleExclusionIn(BaseModel):
    datetime: datetime


class ScheduleExclusionOut(BaseModel):
    datetime: datetime

    class Config:
        from_attributes = True


class ScheduleDayOut(BaseModel):
    day: str

    class Config:
        from_attributes = True


## TODO: make different dto for patch and create
class ScheduleIn(BaseModel):
    time: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    days: Optional[List[Weekday]] = None


class ScheduleOut(BaseModel):
    id: int
    time: time
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    days: List[ScheduleDayOut]
    exclusions: List[ScheduleExclusionOut]

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
            parsed_time = time(hour=hours, minute=minutes, second=seconds)
        else:
            parsed_time = time_value

        return cls(
            id=obj.id,
            time=parsed_time,
            start_datetime=obj.start_datetime,
            end_datetime=obj.end_datetime,
            days=[ScheduleDayOut.model_validate(d) for d in obj.days],
            exclusions=[ScheduleExclusionOut.model_validate(e) for e in obj.exclusions],
        )
