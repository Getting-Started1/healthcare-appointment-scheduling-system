from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.appointment import Appointment
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

AppointmentOut = pydantic_model_creator(Appointment, name="Appointment")
AppointmentIn = pydantic_model_creator(Appointment, name="AppointmentIn", exclude_readonly=True)

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    start_time: str
    end_time: str
    status: Optional[str] = "scheduled"