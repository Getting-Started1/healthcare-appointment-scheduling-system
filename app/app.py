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
#Get Requests
@app.get('/patient')
async def get_all_patients():
    response = await patient_pydantic.from_queryset(Patient.all())
    return {"status": "ok", "data": response}


@app.get('/patient/{patient_id}')
async def get_specific_patient(patient_id: int):
    response = await patient_pydantic.from_queryset_single(Patient.get(id=patient_id))
    return {"status": "ok", "data": response}

# Update Patient
@app.put('/patient/{patient_id}')
async def update_patient(patient_id: int, update_info: patient_pydanticIn):
    patient = await Patient.get(id=patient_id)
    update_info = update_info.dict(exclude_unset=True)
    patient.name = update_info['name']
    patient.email = update_info['email']
    patient.phone = update_info['phone']
    patient.insurance_info = update_info['insurance_info']
    await patient.save()
    response = await patient_pydantic.from_tortoise_orm(patient)
    return {"status": "ok", "data": response}
     
#Delete Patient
@app.delete('/patient/{patient_id}')
async def delete_patient(patient_id: int):
    delete_count = await Patient.filter(id=patient_id).delete()
    if delete_count == 0:
        return{"status": "error", "message": "Patient not found"}
         
    return{"status": "ok", "message": "Patient deleted successfully"}
    
         
     
     
#Create a Doctor
@app.post('/doctor')
async def add_doctor(doctor_info: doctor_pydanticIn):
    doctor_obj = await Doctor.create(**doctor_info.dict(exclude_unset=True))
    response = await doctor_pydantic.from_tortoise_orm(doctor_obj)
    return {"status": "ok", "data": response}


#Get Requests
@app.get('/doctors')
async def get_all_doctors():
    response = await doctor_pydantic.from_queryset(Doctor.all())
    return {"status": "ok", "data": response}


@app.get('/doctor/{doctor_id}')
async def get_specific_doctor(doctor_id: int):
    response = await doctor_pydantic.from_queryset_single(Doctor.get(id=doctor_id))
    return {"status": "ok", "data": response}


# Update Patient
@app.put('/doctor/{doctor_id}')
async def update_doctor(doctor_id: int, update_info: doctor_pydanticIn):
    doctor = await Doctor.get(id=doctor_id)
    update_info = update_info.dict(exclude_unset=True)
    doctor.name = update_info['name']
    doctor.specialization = update_info['specialization']
    doctor.contact = update_info['contact']
    await doctor.save()
    response = await doctor_pydantic.from_tortoise_orm(doctor)
    return {"status": "ok", "data": response}
     











#Create Appointment

@app.post('/appointment')
async def add_appointment(appointment_info: appointment_pydanticIn):
    appointment_obj = await Appointment.create(**appointment_info.dict(exclude_unset=True))
    response = await appointment_pydantic.from_tortoise_orm(appointment_obj)
    return {"status": "ok", "data": response}

# MedicalRecords
# Post Request 
@app.post('/medicalrecord')
async def add_medicalrecord(medicalrecord_info: medicalrecord_pydanticIn):
    medicalrecord_obj = await MedicalRecord.create(**medicalrecord_info.dict(exclude_unset=True))
    response = await medicalrecord_pydantic.from_tortoise_orm(medicalrecord_obj)
    return {"status": "ok", "data": response}


#Tortoise ORM setup
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,   
)


    