from tortoise.models import Model
from tortoise import fields
from app.models.user import User

class Doctor(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", 
        related_name="doctor_profile",
        on_delete=fields.CASCADE
    )
    specialization = fields.CharField(max_length=255)
    contact = fields.CharField(max_length=20)
    experience = fields.IntField(default=0)  # Years of experience
    fees = fields.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Consultation fees
    
    class Meta:
        table = "doctors"
        unique_together = ("user", "specialization")  # Ensures one doctor profile per user

    def __str__(self):
        return f"Dr. {self.user.full_name()} ({self.specialization})"