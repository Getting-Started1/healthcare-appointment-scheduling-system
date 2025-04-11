from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.patient import Patient
from pydantic import BaseModel

PatientOut = pydantic_model_creator(Patient, name="Patient")
PatientIn = pydantic_model_creator(Patient, name="PatientIn", exclude_readonly=True)


class PatientUpdate(BaseModel):
    name: str
    email: str
    phone: str
    insurance_info: str
    class Config:
        extra = "forbid"