from tortoise.contrib.pydantic import pydantic_model_creator
from app.models.patient import Patient

PatientOut = pydantic_model_creator(Patient, name="Patient")
PatientIn = pydantic_model_creator(Patient, name="PatientIn", exclude_readonly=True)