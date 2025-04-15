from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import DoesNotExist
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate
from app.utils.auth import get_current_active_user, get_current_doctor, get_current_admin
from app.models.user import User, UserRole


router = APIRouter(prefix="/patients", tags=["patients"])

# ADMIN-ONLY ENDPOINTS
@router.post("/", response_model=PatientOut)
async def create_patient(
    patient: PatientCreate,
    current_user: User = Depends(get_current_active_user)
):
    # Check if user already has a patient profile
    existing_patient = await Patient.get_or_none(user_id=current_user.id)
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a patient profile"
        )
    
    # Only allow patients to create their own profile or doctors/admins to create any profile
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patients can only create their own profile"
        )
    
    # Create the patient profile
    patient_obj = await Patient.create(**patient.dict())
    return await PatientOut.from_tortoise_orm(patient_obj)

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: int,
    current_user: User = Depends(get_current_admin)  # Only admins can delete
):
    deleted_count = await Patient.filter(id=patient_id).delete()
    if not deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return {"message": f"Deleted patient {patient_id}"}

# DOCTOR-ACCESSIBLE ENDPOINTS
@router.get("/", response_model=list[PatientOut])
async def get_all_patients(
    current_user: User = Depends(get_current_doctor)  # Doctors can list patients
):
    return await PatientOut.from_queryset(Patient.all())

# PATIENT-SPECIFIC ACCESS
@router.get("/{patient_id}", response_model=PatientOut)
async def get_patient(
    patient_id: int,
    current_user: User = Depends(get_current_active_user)
):
    try:
        patient = await Patient.get(id=patient_id)
        
        # Patients can only view their own records
        if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this patient record"
            )
            
        return await PatientOut.from_tortoise_orm(patient)
        
    except DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )

@router.put("/{patient_id}", response_model=PatientOut)
async def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_active_user)
):
    # Verify patient exists
    patient = await Patient.get_or_none(id=patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Authorization check
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Patients can only update their own records"
        )

    # Get the data to update
    update_data = patient_data.dict(exclude_unset=True)
    
    # Handle special case where name/email are being updated
    # These should update the associated user record
    if "name" in update_data or "email" in update_data:
        user = await User.get(id=patient.user_id)
        if "name" in update_data:
            # Split name into firstname and lastname
            name_parts = update_data.pop("name").split(" ", 1)
            if len(name_parts) > 1:
                user.firstname = name_parts[0]
                user.lastname = name_parts[1]
            else:
                user.firstname = name_parts[0]
        if "email" in update_data:
            user.email = update_data.pop("email")
        await user.save()
    
    # Update patient record with remaining fields
    if update_data:
        await Patient.filter(id=patient_id).update(**update_data)
    
    return await PatientOut.from_tortoise_orm(await Patient.get(id=patient_id))