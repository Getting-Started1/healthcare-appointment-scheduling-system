from tortoise.models import Model
from tortoise import fields

    
class MedicalRecord(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("models.Patient", related_name="medical_records")
    appointment = fields.ForeignKeyField("models.Appointment", related_name="medical_record")
    diagnosis = fields.TextField()
    prescription = fields.TextField()
    doctor = fields.ForeignKeyField("models.User", related_name="created_records")
