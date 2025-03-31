from tortoise.models import Model
from tortoise import fields


class Doctor(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length= 255,unique=True)
    specialization = fields.CharField(max_length= 255)
    contact = fields.CharField(max_length= 20)
    appointments = fields.ReverseRelation["Appointment"] # one to Many
