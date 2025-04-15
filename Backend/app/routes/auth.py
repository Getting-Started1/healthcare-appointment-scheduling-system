from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import ValidationError
from app.models.user import User
from app.schemas.auth import (
    Token, UserCreate, UserOut, LoginForm, UserRole, UserInDB
)
from app.utils.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user,
    get_current_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from tortoise.exceptions import IntegrityError
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "sub": user.username,
            "role": user.role.value  # Include role in token
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_with_role(login_data: LoginForm):
    # Find user by email
    user = await User.get_or_none(email=login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify role matches
    if user.role.value != login_data.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is not a {login_data.role}"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "sub": user.username,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
async def register_user(user_data: UserCreate):
    try:
        # Check if email already exists
        if await User.filter(email=user_data.email).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate username from email (remove @ and everything after)
        username = user_data.email.split('@')[0]
        
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user
        user = await User.create(
            username=username,  # Generated username
            email=user_data.email,
            hashed_password=hashed_password,
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            role=user_data.role,
            profile_picture=user_data.profile_picture,
            disabled=False
        )
        
        return user
        
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database error occurred"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user/getuser/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # Replace UserOut.from_orm(user) with:
    return UserOut.model_validate(user)

@router.get("/users", response_model=List[UserOut])
async def get_users(current_user: User = Depends(get_current_admin)):
    """Get all users. Only accessible by admin."""
    users = await User.all()
    return [UserOut.model_validate(user) for user in users]