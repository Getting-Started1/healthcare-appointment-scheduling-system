from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from tortoise.exceptions import DoesNotExist
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentOut, AppointmentCreate
from app.models.user import User
from app.utils.auth import get_current_active_user



router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentOut)
async def create_appointment(appointment: AppointmentCreate, current_user: User = Depends(get_current_active_user)):
    # Check patient exists
    if not await Patient.filter(id=appointment.patient_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {appointment.patient_id} not found"
        )
    
    # Check doctor exists
    if not await Doctor.filter(id=appointment.doctor_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {appointment.doctor_id} not found"
        )
    
    # Parse datetimes
    try:
        start_time = datetime.fromisoformat(appointment.start_time)
        end_time = datetime.fromisoformat(appointment.end_time)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    # Create appointment
    appointment_obj = await Appointment.create(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        start_time=start_time,
        end_time=end_time,
        status=appointment.status
    )
    return await AppointmentOut.from_tortoise_orm(appointment_obj)

@router.get("/", response_model=list[AppointmentOut])
async def get_all_appointments(current_user: User = Depends(get_current_active_user)):
    return await AppointmentOut.from_queryset(Appointment.all())

@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(appointment_id: int, current_user: User = Depends(get_current_active_user)):
    try:
        return await AppointmentOut.from_queryset_single(Appointment.get(id=appointment_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )