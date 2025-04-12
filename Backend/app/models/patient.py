from tortoise.models import Model
from tortoise import fields
from app.models.user import User

class Patient(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    phone = fields.CharField(max_length=20)
    insurance_info = fields.TextField(null=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", related_name="patient")
    appointments = fields.ReverseRelation["Appointment"]