from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorIn, DoctorOut
from app.models.user import User
from app.utils.auth import get_current_doctor

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.post("/", response_model=DoctorOut)
async def create_doctor(
    doctor: DoctorIn,
     current_user: User = Depends(get_current_doctor)
    ):
    doctor_obj = await Doctor.create(**doctor.dict(exclude_unset=True))
    return await DoctorOut.from_tortoise_orm(doctor_obj)

@router.get("/", response_model=list[DoctorOut])
async def get_all_doctors(current_user: User = Depends(get_current_active_user)):
    return await DoctorOut.from_queryset(Doctor.all())

@router.get("/{doctor_id}", response_model=DoctorOut)
async def get_doctor(doctor_id: int,  current_user: User = Depends(get_current_active_user)):
    try:
        return await DoctorOut.from_queryset_single(Doctor.get(id=doctor_id))
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {doctor_id} not found"
        )

@router.put("/{doctor_id}", response_model=DoctorOut)
async def update_doctor(doctor_id: int, doctor: DoctorIn,  current_user: User = Depends(get_current_active_user)):
    await Doctor.filter(id=doctor_id).update(**doctor.dict(exclude_unset=True))
    return await DoctorOut.from_queryset_single(Doctor.get(id=doctor_id))

@router.delete("/{doctor_id}")
async def delete_doctor(doctor_id: int, current_user: User = Depends(get_current_active_user)):
    deleted_count = await Doctor.filter(id=doctor_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor {doctor_id} not found"
        )
    return {"message": f"Deleted doctor {doctor_id}"}