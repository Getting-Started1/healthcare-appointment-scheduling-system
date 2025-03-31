from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserBase(BaseModel):
    username: str
    
class UserCreate(UserBase):
    password: str
    
class UserInDB(UserBase):
    hashed_password: str
    disabled: bool
    