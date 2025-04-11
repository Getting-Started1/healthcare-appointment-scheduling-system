from enum import Enum
from tortoise.models import Model
from tortoise import fields

class UserRole(str, Enum):
    PATIENT = "Patient"
    DOCTOR = "Doctor"
    ADMIN = "Admin"

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    firstname = fields.CharField(max_length=255)
    lastname = fields.CharField(max_length=255)
    role = fields.CharEnumField(UserRole, default=UserRole.PATIENT)
    profile_picture = fields.CharField(max_length=500, null=True)
    disabled = fields.BooleanField(default=False)
    
    class Meta:
        table = "users"
        
    def full_name(self):
        return f"{self.firstname} {self.lastname}"