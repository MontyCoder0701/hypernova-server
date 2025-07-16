from tortoise import Model, fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class Schedule(Model):
    id = fields.IntField(pk=True)
    days = fields.JSONField()
    time = fields.TimeField()
    is_active = fields.BooleanField(default=True)
    start_date = fields.DateField()
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="schedules", on_delete=fields.CASCADE
    )
