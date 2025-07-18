from tortoise import fields, models

from model.schedule import Schedule


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    schedules: fields.ReverseRelation["Schedule"]
