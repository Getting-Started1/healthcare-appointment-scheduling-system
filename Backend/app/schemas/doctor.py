from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.doctor import Doctor
from pydantic import BaseModel, condecimal

DoctorOut = pydantic_model_creator(Doctor, name="Doctor")
DoctorIn = pydantic_model_creator(Doctor, name="DoctorIn", exclude_readonly=True)

class DoctorCreate(BaseModel):
    user_id: int
    username: str
    specialization: str
    contact: str
    experience: int = 0
    fees: condecimal(max_digits=10, decimal_places=2) = 0.00