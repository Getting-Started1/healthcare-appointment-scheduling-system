from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.schemas.medical_record import MedicalRecordOut, MedicalRecordCreate
from app.models.user import User
from app.utils.auth import get_current_active_user, get_current_doctor
import logging

router = APIRouter(prefix="/medical-records", tags=["medical_records"])
logger = logging.getLogger(__name__)

# DOCTOR-ONLY ENDPOINTS
@router.post("/", response_model=MedicalRecordOut)
async def create_medical_record(
    record: MedicalRecordCreate,
    current_user: User = Depends(get_current_doctor)  # Only doctors can create
):
    # Verify patient exists
    patient = await Patient.get_or_none(id=record.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    # Verify appointment exists and belongs to patient
    appointment = await Appointment.get_or_none(id=record.appointment_id)
    if not appointment or appointment.patient_id != record.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment for patient"
        )

    # Verify the current doctor was involved in the appointment
    if appointment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create records for this appointment"
        )

    record_obj = await MedicalRecord.create(
        patient_id=record.patient_id,
        appointment_id=record.appointment_id,
        doctor_id=current_user.id,  # Track which doctor created it
        diagnosis=record.diagnosis,
        prescription=record.prescription
    )
    
    logger.info(f"Doctor {current_user.id} created record for patient {record.patient_id}")
    return await MedicalRecordOut.from_tortoise_orm(record_obj)

# ROLE-BASED ACCESS ENDPOINTS
@router.get("/", response_model=list[MedicalRecordOut])
async def get_all_medical_records(
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role == "patient":
        return await MedicalRecordOut.from_queryset(
            MedicalRecord.filter(patient_id=current_user.id)
        )
    elif current_user.role == "doctor":
        return await MedicalRecordOut.from_queryset(
            MedicalRecord.filter(doctor_id=current_user.id)
        )
    else:  # admin
        return await MedicalRecordOut.from_queryset(MedicalRecord.all())

@router.get("/{record_id}", response_model=MedicalRecordOut)
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user)
):
    record = await MedicalRecord.get_or_none(id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found"
        )

    # Authorization checks
    if current_user.role == "patient" and record.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this record"
        )
    
    if current_user.role == "doctor" and record.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this record"
        )

    logger.info(f"User {current_user.id} accessed record {record_id}")
    return await MedicalRecordOut.from_tortoise_orm(record)