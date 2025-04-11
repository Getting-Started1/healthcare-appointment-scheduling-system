from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from tortoise.exceptions import DoesNotExist, IntegrityError
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.appointment import AppointmentOut, AppointmentCreate
from app.models.user import User
from app.utils.auth import get_current_active_user, get_current_doctor
from pydantic import ValidationError

router = APIRouter(prefix="/appointments", tags=["appointments"])

@router.post("/", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_doctor)
):
    # Inside the create_appointment function
    appointment.start_time = datetime.fromisoformat(appointment.start_time)
    appointment.end_time = datetime.fromisoformat(appointment.end_time)

    
    """Create a new appointment with conflict checking"""
    # Verify patient exists
    patient = await Patient.get_or_none(id=appointment.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Verify doctor exists and matches current user
    doctor = await Doctor.get_or_none(id=appointment.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    if doctor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only create appointments for yourself"
        )

    # Validate time range
    if appointment.end_time <= appointment.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check minimum appointment duration (e.g., 15 minutes)
    min_duration = timedelta(minutes=15)
    if (appointment.end_time - appointment.start_time) < min_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum appointment duration is {min_duration.seconds//60} minutes"
        )

    # Check for scheduling conflicts
    conflicting = await Appointment.filter(
        doctor_id=appointment.doctor_id,
        start_time__lt=appointment.end_time,
        end_time__gt=appointment.start_time,
        status__not_in=["cancelled", "completed"]
    ).exists()

    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot already booked"
        )

    # Create appointment
    try:
        appointment_obj = await Appointment.create(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status
        )
        return await AppointmentOut.from_tortoise_orm(appointment_obj)
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error"
        )

@router.patch("/{appointment_id}/status", status_code=status.HTTP_200_OK)
async def update_status(
    appointment_id: int,
    new_status: str = Body(..., embed=True),
    current_user: User = Depends(get_current_doctor)
):
    """Update appointment status (scheduled/completed/cancelled)"""
    valid_statuses = ["scheduled", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    appointment = await Appointment.get_or_none(id=appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    print(f"Doctor ID from appointment: {appointment.doctor_id}")  # Debugging log
    print(f"Current user ID: {current_user.id}")  # Debugging log
    
    if appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify appointments you created"
        )

    await Appointment.filter(id=appointment_id).update(status=new_status)
    return {"message": f"Status updated to {new_status}"}
    # Update the appointment status
    await Appointment.filter(id=appointment_id).update(status=new_status)

    return {"message": f"Status updated to {new_status}"}


@router.get("/", response_model=list[AppointmentOut])
async def get_all_appointments(
    current_user: User = Depends(get_current_active_user)
):
    """Get all appointments"""
    return await AppointmentOut.from_queryset(Appointment.all())

@router.get("/{appointment_id}", response_model=AppointmentOut)
async def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific appointment details"""
    appointment = await Appointment.get_or_none(id=appointment_id)
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Patients can only view their own appointments
    if current_user.role == "patient" and appointment.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view your own appointments"
        )
    
    return await AppointmentOut.from_tortoise_orm(appointment)