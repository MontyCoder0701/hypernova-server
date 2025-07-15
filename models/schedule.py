from tortoise import fields
from tortoise.models import Model


class Schedule(Model):
    id = fields.IntField(pk=True)
    days = fields.JSONField()
    time = fields.TimeField()
    is_active = fields.BooleanField(default=True)
    start_date = fields.DateField()
