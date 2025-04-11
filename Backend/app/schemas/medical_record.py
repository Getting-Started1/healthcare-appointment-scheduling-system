from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.medical_record import MedicalRecord
from pydantic import BaseModel


MedicalRecordOut = pydantic_model_creator(MedicalRecord, name="MedicalRecord")
MedicalRecordIn = pydantic_model_creator(MedicalRecord, name="MedicalRecordIn", exclude_readonly=True)

class MedicalRecordCreate(BaseModel):
    patient_id: int
    appointment_id: int
    diagnosis: str
    prescription: str