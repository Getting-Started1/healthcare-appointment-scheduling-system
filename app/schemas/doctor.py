from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.doctor import Doctor

DoctorOut = pydantic_model_creator(Doctor, name="Doctor")
DoctorIn = pydantic_model_creator(Doctor, name="DoctorIn", exclude_readonly=True)