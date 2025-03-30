from tortoise.models import Model
from tortoise import fields


class Patient(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    email = fields.CharField(max_length = 255, unique= True)
    phone = fields.CharField(max_length = 20)
    insurance_info = fields.TextField(null=True)
    appointments = fields.ReverseRelation["Appointment"] # one to Many

class Doctor(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length= 255,unique=True)
    specialization = fields.CharField(max_length= 255)
    contact = fields.CharField(max_length= 20)
    appointments = fields.ReverseRelation["Appointment"] # one to Many
    
class Appointment(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("models.Patient", related_name='appointments')
    doctor =  fields.ForeignKeyField("models.Doctor", related_name="appintments")
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    status = fields.CharField(max_length =50, default="scheduled")
    medical_record = fields.ReverseRelation["MedicalRecord"] # One to Many
    
class MedicalRecord(Model):
    id = fields.IntField(pk=True)
    patient = fields.ForeignKeyField("models.Patient", related_name="medical_record")
    appointment = fields.ForeignKeyField("models.Appointment", related_name="medical_record")
    diagnosis = fields.TextField()
    prescription = fields.TextField()

        