from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.schemas.medical_record import MedicalRecordOut, MedicalRecordCreate
from app.models.user import User
from app.utils.auth import get_current_active_user


router = APIRouter(prefix="/medical-records", tags=["medical_records"])

@router.post("/", response_model=MedicalRecordOut)
async def create_medical_record(record: MedicalRecordCreate, current_user: User = Depends(get_current_active_user)):
    # Check patient exists
    if not await Patient.filter(id=record.patient_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {record.patient_id} not found"
        )
    
    # Check appointment exists
    if not await Appointment.filter(id=record.appointment_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {record.appointment_id} not found"
        )
    
    # Create medical record
    record_obj = await MedicalRecord.create(
        patient_id=record.patient_id,
        appointment_id=record.appointment_id,
        diagnosis=record.diagnosis,
        prescription=record.prescription
    )
    return await MedicalRecordOut.from_tortoise_orm(record_obj)

@router.get("/", response_model=list[MedicalRecordOut])
async def get_all_medical_records(current_user: User = Depends(get_current_active_user)):
    return await MedicalRecordOut.from_queryset(MedicalRecord.all())

@router.get("/{record_id}", response_model=MedicalRecordOut)
async def get_medical_record(
    record_id: int,
    current_user: User = Depends(get_current_active_user)                         
    ):
    try:
        return await MedicalRecordOut.from_queryset_single(MedicalRecord.get(id=record_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medical record {record_id} not found"
        )