from enum import IntEnum
from tortoise import Model, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Weekday(IntEnum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class Schedule(Model):
    id = fields.IntField(pk=True)
    time = fields.TimeField()
    start_datetime = fields.DatetimeField()
    end_datetime = fields.DatetimeField(null=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="schedules", on_delete=fields.CASCADE
    )


class ScheduleDay(Model):
    id = fields.IntField(pk=True)
    day = fields.IntEnumField(enum_type=Weekday)
    schedule: fields.ForeignKeyRelation[Schedule] = fields.ForeignKeyField(
        "models.Schedule", related_name="days", on_delete=fields.CASCADE
    )


class ScheduleExclusion(Model):
    id = fields.IntField(pk=True)
    datetime = fields.DatetimeField()
    schedule: fields.ForeignKeyRelation[Schedule] = fields.ForeignKeyField(
        "models.Schedule", related_name="exclusions", on_delete=fields.CASCADE
    )


class ScheduleTimeModification(Model):
    id = fields.IntField(pk=True)
    datetime = fields.DatetimeField()
    schedule: fields.ForeignKeyRelation[Schedule] = fields.ForeignKeyField(
        "models.Schedule", related_name="time_modifications", on_delete=fields.CASCADE
    )
