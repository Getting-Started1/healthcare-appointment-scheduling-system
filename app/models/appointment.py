from tortoise.models import Model
from tortoise import fields

class Appointment(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("models.Patient", related_name='appointments')
    doctor = fields.ForeignKeyField("models.Doctor", related_name="appointments")
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    status = fields.CharField(
        max_length=20,
        default="scheduled",
        choices=["scheduled", "completed", "cancelled"]
    )
    
    class Meta:
        table = "appointments"
        
    