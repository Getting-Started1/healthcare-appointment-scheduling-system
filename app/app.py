# from fastapi import FastAPI
# from tortoise.contrib.fastapi import register_tortoise
# from app.models import (patient_pydantic,patient_pydanticIn, Patient, doctor_pydantic,doctor_pydanticIn,Doctor, appointment_pydantic,appointment_pydanticIn, Appointment, medicalrecord_pydantic, medicalrecord_pydanticIn, MedicalRecord)
# from fastapi import HTTPException, status
# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime





# app = FastAPI()

# @app.get('/')

# def index():
#     return {"Msg": "go to / docs for the api documentation"}

# # Create a Patient
# @app.post('/patient')
# async def add_patient(patient_info: patient_pydanticIn):
#     patient_obj = await Patient.create(**patient_info.dict(exclude_unset=True))
#     response = await patient_pydantic.from_tortoise_orm(patient_obj)
#     return {"status": "ok", "data": response}
# #Get Requests
# @app.get('/patient')
# async def get_all_patients():
#     response = await patient_pydantic.from_queryset(Patient.all())
#     return {"status": "ok", "data": response}


# @app.get('/patient/{patient_id}')
# async def get_specific_patient(patient_id: int):
#     response = await patient_pydantic.from_queryset_single(Patient.get(id=patient_id))
#     return {"status": "ok", "data": response}

# # Update Patient
# @app.put('/patient/{patient_id}')
# async def update_patient(patient_id: int, update_info: patient_pydanticIn):
#     patient = await Patient.get(id=patient_id)
#     update_info = update_info.dict(exclude_unset=True)
#     patient.name = update_info['name']
#     patient.email = update_info['email']
#     patient.phone = update_info['phone']
#     patient.insurance_info = update_info['insurance_info']
#     await patient.save()
#     response = await patient_pydantic.from_tortoise_orm(patient)
#     return {"status": "ok", "data": response}
     
# #Delete Patient
# @app.delete('/patient/{patient_id}')
# async def delete_patient(patient_id: int):
#     delete_count = await Patient.filter(id=patient_id).delete()
#     if delete_count == 0:
#         return{"status": "error", "message": "Patient not found"}
         
#     return{"status": "ok", "message": "Patient deleted successfully"}
    
         
     
     
# #Create a Doctor
# @app.post('/doctor')
# async def add_doctor(doctor_info: doctor_pydanticIn):
#     doctor_obj = await Doctor.create(**doctor_info.dict(exclude_unset=True))
#     response = await doctor_pydantic.from_tortoise_orm(doctor_obj)
#     return {"status": "ok", "data": response}


# #Get Requests
# @app.get('/doctors')
# async def get_all_doctors():
#     response = await doctor_pydantic.from_queryset(Doctor.all())
#     return {"status": "ok", "data": response}


# @app.get('/doctor/{doctor_id}')
# async def get_specific_doctor(doctor_id: int):
#     response = await doctor_pydantic.from_queryset_single(Doctor.get(id=doctor_id))
#     return {"status": "ok", "data": response}


# # Update Doctor
# @app.put('/doctor/{doctor_id}')
# async def update_doctor(doctor_id: int, update_info: doctor_pydanticIn):
#     doctor = await Doctor.get(id=doctor_id)
#     update_info = update_info.dict(exclude_unset=True)
#     doctor.name = update_info['name']
#     doctor.specialization = update_info['specialization']
#     doctor.contact = update_info['contact']
#     await doctor.save()
#     response = await doctor_pydantic.from_tortoise_orm(doctor)
#     return {"status": "ok", "data": response}
     

# #Delete Doctor
# @app.delete('/doctor/{doctor_id}')
# async def delete_doctor(doctor_id: int):
#     delete_count = await Doctor.filter(id=doctor_id).delete()
#     if delete_count == 0:
#         return{"status": "error", "message": "Doctor not found"}
         
#     return{"status": "ok", "message": "Doctor deleted successfully"}




# #Helper Class for datetime validation
# class AppointmentCreate(BaseModel):
#     patient_id: int
#     doctor_id: int
#     start_time: str  # ISO format datetime string
#     end_time: str    # ISO format datetime string
#     status: Optional[str] = "scheduled"

# # Create Appointment - Fixed Version
# @app.post('/appointment')
# async def add_appointment(appointment_data: AppointmentCreate):
#     try:
#         # Validate patient existence
#         patient = await Patient.get_or_none(id=appointment_data.patient_id)
#         if not patient:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Patient not found"
#             )

#         # Validate doctor existence
#         doctor_obj = await Doctor.get_or_none(id=appointment_data.doctor_id)
#         if not doctor_obj:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Doctor not found"
#             )

#         # Parse datetime strings
#         try:
#             start_time = datetime.fromisoformat(appointment_data.start_time)
#             end_time = datetime.fromisoformat(appointment_data.end_time)
#         except ValueError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS). Error: {str(e)}"
#             )

#         # Check if end time is after start time
#         if end_time <= start_time:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="End time must be after start time"
#             )

#         # Check for time conflicts
#         conflicting_appointment = await Appointment.filter(
#             doctor_id=appointment_data.doctor_id,
#             start_time__lt=end_time,
#             end_time__gt=start_time
#         ).exists()

#         if conflicting_appointment:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail="Doctor already has an appointment during this time slot"
#             )

#         # Create appointment
#         appointment = await Appointment.create(
#             patient_id=appointment_data.patient_id,
#             doctor_id=appointment_data.doctor_id,
#             start_time=start_time,
#             end_time=end_time,
#             status=appointment_data.status
#         )

#         response = await appointment_pydantic.from_tortoise_orm(appointment)
#         return {"status": "ok", "data": response}

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"An error occurred while creating appointment: {str(e)}"
#         )
# #Get Requests
# @app.get('/appointment')
# async def get_all_appointmentS():
#     response = await appointment_pydantic.from_queryset(Appointment.all())
#     return {"status": "ok", "data": response}


# @app.get('/appointment/{appointment_id}')
# async def get_specific_patient(appointment_id: int):
#     appointment = await Appointment.get_or_none(id=appointment_id)
#     if not appointment:
#         return {"status":"error","message":"Appointment not found"}
#     response = await appointment_pydantic.from_tortoise_orm(appointment)
#     return{"status":"ok", "data": response}




# # MedicalRecords
# class MedicalRecordCreate(BaseModel):
#     patient_id: int
#     appointment_id: int
#     diagnosis: str
#     prescription: str

# @app.post('/medicalrecord')
# async def add_medicalrecord(record_data: MedicalRecordCreate):
#     try:
#         # Validate patient existence
#         patient = await Patient.get_or_none(id=record_data.patient_id)
#         if not patient:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Patient not found"
#             )

#         # Validate appointment existence
#         appointment = await Appointment.get_or_none(id=record_data.appointment_id)
#         if not appointment:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Appointment not found"
#             )

#         # Check if appointment belongs to patient
#         if appointment.patient_id != patient.id:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Appointment does not belong to this patient"
#             )

#         # Create medical record
#         record = await MedicalRecord.create(
#             patient=patient,
#             appointment=appointment,
#             diagnosis=record_data.diagnosis,
#             prescription=record_data.prescription
#         )

#         response = await medicalrecord_pydantic.from_tortoise_orm(record)
#         return {"status": "ok", "data": response}

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )
# #Get Requests
# @app.get('/medicalrecords')
# async def get_all_medicalrecord():
#     response = await medicalrecord_pydantic.from_queryset(MedicalRecord.all())
#     return {"status": "ok", "data": response}





# #Tortoise ORM setup
# register_tortoise(
#     app,
#     db_url="sqlite://db.sqlite3",
#     modules={"models": ["app.models"]},
#     generate_schemas=True,
#     add_exception_handlers=True,   
# )


    