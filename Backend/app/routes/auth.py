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

router = APIRouter(prefix="/auth", tags=["Authentication"])

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

@router.post("/login", response_model=Token,
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": 401,
                            "message": "Incorrect email or password",
                            "type": "AuthenticationError"
                        }
                    }
                }
            }
        }
    })
async def login_with_role(form_data: LoginForm = Body(..., example={
    "email": "john@example.com",
    "password": "strongpassword123",
    "role": "Patient"
})):
    """
    Authenticate a user and return a JWT token.
    
    - **email**: User's email address
    - **password**: User's password
    - **role**: User's role (Admin, Doctor, or Patient)
    
    Returns a JWT token for authenticated requests.
    """
    user = await authenticate_user(form_data.email, form_data.password, form_data.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "Patient",
                        "profile_picture": "https://example.com/pic.jpg"
                    }
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": 400,
                            "message": "Email already registered",
                            "type": "ValidationError"
                        }
                    }
                }
            }
        }
    })
async def register_user(user_data: UserCreate = Body(..., example={
    "username": "john_doe",
    "email": "john@example.com",
    "password": "strongpassword123",
    "role": "Patient",
    "profile_picture": "https://example.com/pic.jpg"
})):
    """
    Register a new user in the system.
    
    - **username**: Unique username for the user
    - **email**: Valid email address
    - **password**: Strong password (min 6 characters)
    - **role**: User role (Admin, Doctor, or Patient)
    - **profile_picture**: Optional URL to user's profile picture
    
    Returns the created user without sensitive information.
    """
    try:
        # Check if email already exists
        if await User.filter(email=user_data.email).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await User.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=get_password_hash(user_data.password),
            role=user_data.role,
            profile_picture=user_data.profile_picture
        )
        
        return UserOut.model_validate(user)
        
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/user/getuser/{user_id}", response_model=UserOut,
    responses={
        200: {
            "description": "User found",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "role": "Patient",
                        "profile_picture": "https://example.com/pic.jpg"
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": {
                            "code": 404,
                            "message": "User not found",
                            "type": "NotFoundError"
                        }
                    }
                }
            }
        }
    })
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    """
    Get user details by ID.
    
    - **user_id**: ID of the user to retrieve
    
    Returns user details if found.
    Requires authentication.
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has permission to view this profile
    if current_user.role != "Admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )
    
    return UserOut.model_validate(user)

@router.get("/users", response_model=List[UserOut])
async def get_users(current_user: User = Depends(get_current_admin)):
    """Get all users. Only accessible by admin."""
    users = await User.all()
    return [UserOut.model_validate(user) for user in users]