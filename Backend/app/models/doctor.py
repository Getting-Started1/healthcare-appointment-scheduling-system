from tortoise.models import Model
from tortoise import fields

class Doctor(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User", 
        related_name="doctor_profile",
        on_delete=fields.CASCADE
    )
    name = fields.CharField(max_length=255)  # Removed unique
    specialization = fields.CharField(max_length=255)
    contact = fields.CharField(max_length=20)
    
    class Meta:
        table = "doctors"
        unique_together = ("user", "name")  # Ensures one doctor profile per user

    def __str__(self):
        return f"{self.name} ({self.specialization})"