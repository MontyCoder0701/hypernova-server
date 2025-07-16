from tortoise import Model, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Schedule(Model):
    id = fields.IntField(pk=True)
    time = fields.TimeField()
    start_date = fields.DateField()
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="schedules", on_delete=fields.CASCADE
    )


class ScheduleDay(Model):
    id = fields.IntField(pk=True)
    day = fields.CharField(max_length=9)
    schedule: fields.ForeignKeyRelation[Schedule] = fields.ForeignKeyField(
        "models.Schedule", related_name="days", on_delete=fields.CASCADE
    )


class ScheduleExclusion(Model):
    id = fields.IntField(pk=True)
    datetime = fields.DatetimeField()
    schedule: fields.ForeignKeyRelation[Schedule] = fields.ForeignKeyField(
        "models.Schedule", related_name="exclusions", on_delete=fields.CASCADE
    )
