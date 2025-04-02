from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserCreate
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(tags=["auth"])


router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut)
async def register_user(
    user_data: UserCreate,
    role: UserRole = UserRole.PATIENT
):
    """
    Register a new user
    - Default role is PATIENT
    - Returns user ID for profile creation
    - For doctors: Use returned ID to create doctor profile via /doctors endpoint
    """
    existing_user = await User.get_or_none(username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    hashed_password = get_password_hash(user_data.password)
    user = await User.create(
        username=user_data.username,
        hashed_password=hashed_password,
        role=role.value
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "message": f"User created successfully. Next: Create {role.value} profile" 
    }