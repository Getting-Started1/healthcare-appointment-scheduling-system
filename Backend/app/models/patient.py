from tortoise.models import Model
from tortoise import fields

class Patient(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length = 255, unique= True)
    phone = fields.CharField(max_length = 20)
    insurance_info = fields.TextField(null=True)
    appointments = fields.ReverseRelation["Appointment"] # one to Many
