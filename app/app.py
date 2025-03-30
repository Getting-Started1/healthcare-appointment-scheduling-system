from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.models import (patient_pydantic,patient_pydanticIn, Patient, doctor_pydantic,doctor_pydanticIn,Doctor, appointment_pydantic,appointment_pydanticIn, Appointment, medicalrecord_pydantic, medicalrecord_pydanticIn, MedicalRecord)


app = FastAPI()

@app.get('/')

def index():
    return {"Msg": "go to / docs for the api documentation"}

# Create a Patient
@app.post('/patient')
async def add_patient(patient_info: patient_pydanticIn):
    patient_obj = await Patient.create(**patient_info.dict(exclude_unset=True))
    response = await patient_pydantic.from_tortoise_orm(patient_obj)
    return {"status": "ok", "data": response}
     


#Tortoise ORM setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,   
)


    