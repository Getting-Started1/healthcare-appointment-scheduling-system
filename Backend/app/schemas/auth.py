# schemas/auth.py
from pydantic import BaseModel, EmailStr, validator, field_validator
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "Patient"
    DOCTOR = "Doctor"
    ADMIN = "Admin"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None
    role: str | None = None

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str
    confpassword: str
    role: Optional[str] = "Patient"
    profile_picture: Optional[str] = None

    @field_validator('confpassword')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

    @field_validator('email')
    def email_must_be_valid(cls, v):
        if not v or "@" not in v:
            raise ValueError('Email must be valid')
        return v
    class Config:
        extra = "forbid"
class UserInDB(UserBase):
    hashed_password: str
    disabled: bool = False
    firstname: str
    lastname: str
    role: UserRole
    profile_picture: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    firstname: str
    lastname: str
    email: str
    role: str
    profile_picture: Optional[str] = None
    disabled: bool = False

    class Config:
        from_attributes = True 

class LoginForm(BaseModel):
    email: EmailStr
    password: str
    role: UserRole