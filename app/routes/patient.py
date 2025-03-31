from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.patient import Patient
from app.schemas.patient import PatientIn, PatientOut
from app.utils.auth import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=PatientOut)
async def create_patient(
    patient: PatientIn,
    current_user: User = Depends(get_current_active_user)
):
    patient_obj = await Patient.create(**patient.dict(exclude_unset=True))
    return await PatientOut.from_tortoise_orm(patient_obj)

@router.get("/", response_model=list[PatientOut])
async def get_all_patients(current_user: User = Depends(get_current_active_user)):
    return await PatientOut.from_queryset(Patient.all())

@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(patient_id: int):
    try:
        return await PatientOut.from_queryset_single(Patient.get(id=patient_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(patient_id: int, patient: PatientIn):
    await Patient.filter(id=patient_id).update(**patient.dict(exclude_unset=True))
    return await PatientOut.from_queryset_single(Patient.get(id=patient_id))

@router.delete("/{patient_id}")
async def delete_patient(patient_id: int):
    deleted_count = await Patient.filter(id=patient_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return {"message": f"Deleted patient {patient_id}"}