from enum import Enum
from tortoise.models import Model
from tortoise import fields

class UserRole (str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    disabled = fields.BooleanField(default=False)
    role = fields.CharField(max_length=50, default="patient")
class Meta:
    table = "users"
    
