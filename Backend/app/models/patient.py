from tortoise.models import Model
from tortoise import fields
from app.models.user import User

class Patient(Model):
    id = fields.IntField(pk=True)
    phone = fields.CharField(max_length=20)
    insurance_info = fields.TextField(null=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField("models.User", related_name="patient")
    appointments = fields.ReverseRelation["Appointment"]
    
    class Meta:
        table = "patients"
        
    def __str__(self):
        return f"Patient: {self.user.full_name()}"
        
    @property
    def name(self):
        """Get the patient's full name from the associated user"""
        if self.user:
            return self.user.full_name()
        return None
        
    @property
    def email(self):
        """Get the patient's email from the associated user"""
        if self.user:
            return self.user.email
        return None
        
    @property
    def pic(self):
        """Get the patient's profile picture from the associated user"""
        if self.user:
            return self.user.profile_picture
        return None