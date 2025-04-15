from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.patient import Patient
from pydantic import BaseModel
from typing import Optional

PatientOut = pydantic_model_creator(Patient, name="Patient")
PatientIn = pydantic_model_creator(Patient, name="PatientIn", exclude_readonly=True)

class PatientBase(BaseModel):
    phone: str
    insurance_info: Optional[str] = None

class PatientCreate(PatientBase):
    user_id: int

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    insurance_info: Optional[str] = None

class PatientOut(PatientBase):
    id: int
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    pic: Optional[str] = None

    class Config:
        from_attributes = True