from tortoise.models import Model
from tortoise import fields
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment

class MedicalRecord(Model):
    id = fields.IntField(pk=True)
    patient: fields.ForeignKeyRelation[Patient] = fields.ForeignKeyField("models.Patient", related_name="medical_records")
    appointment: fields.ForeignKeyRelation[Appointment] = fields.ForeignKeyField("models.Appointment", related_name="medical_record")
    doctor: fields.ForeignKeyRelation[Doctor] = fields.ForeignKeyField("models.Doctor", related_name="created_records")
    diagnosis = fields.TextField()
    prescription = fields.TextField()
    
    class Meta:
        table = "medical_records"
        
    def __str__(self):
        return f"Medical Record for {self.patient.user.full_name()} by Dr. {self.doctor.user.full_name()}"
