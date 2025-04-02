from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorIn, DoctorOut
from app.models.user import User
from app.utils.auth import get_current_doctor, get_current_admin, get_current_active_user
import logging

router = APIRouter(prefix="/doctors", tags=["doctors"])
logger = logging.getLogger(__name__)

# ADMIN-ONLY ENDPOINTS
@router.post("/", response_model=DoctorOut)
async def create_doctor(
    doctor: DoctorIn,
    current_user: User = Depends(get_current_admin)  # Only admins can create doctors
):
    # Check if user exists and is a doctor
    user = await User.get_or_none(id=doctor.user_id)
    if not user or user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be registered as a doctor first"
        )

    doctor_obj = await Doctor.create(
        **doctor.dict(exclude_unset=True),
        user_id=doctor.user_id  # Explicit link to user account
    )
    
    logger.info(f"Admin {current_user.id} created doctor profile for user {doctor.user_id}")
    return await DoctorOut.from_tortoise_orm(doctor_obj)

@router.delete("/{doctor_id}")
async def delete_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_admin)  # Admin-only
):
    deleted_count = await Doctor.filter(id=doctor_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    logger.warning(f"Admin {current_user.id} deleted doctor {doctor_id}")
    return {"message": "Doctor profile deleted"}

# DOCTOR-ACCESSIBLE ENDPOINTS
@router.get("/", response_model=list[DoctorOut])
async def get_all_doctors(
    current_user: User = Depends(get_current_active_user)  # Accessible to all authenticated users
):
    return await DoctorOut.from_queryset(Doctor.all())

@router.get("/{doctor_id}", response_model=DoctorOut)
async def get_doctor(
    doctor_id: int,
    current_user: User = Depends(get_current_active_user)
):
    try:
        doctor = await Doctor.get(id=doctor_id)
        
        # Doctors can only view their own full profile
        if current_user.role == "doctor" and doctor.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only view your own doctor profile"
            )
            
        return await DoctorOut.from_tortoise_orm(doctor)
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )

@router.put("/{doctor_id}", response_model=DoctorOut)
async def update_doctor(
    doctor_id: int,
    doctor: DoctorIn,
    current_user: User = Depends(get_current_doctor)  # Doctor can only update self
):
    existing_doctor = await Doctor.get_or_none(id=doctor_id)
    if not existing_doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Verify doctor is updating their own profile
    if existing_doctor.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile"
        )
    
    await Doctor.filter(id=doctor_id).update(**doctor.dict(exclude_unset=True))
    logger.info(f"Doctor {current_user.id} updated their profile")
    return await DoctorOut.from_queryset_single(Doctor.get(id=doctor_id))