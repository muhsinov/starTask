from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import enum

class RoleEnum(str, enum.Enum):
    company_admin = "company_admin"
    department_manager = "department_manager"
    employee = "employee"

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    
class UserCreateWithCompany(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str

    company_name: str
    company_address: str
    company_phone: str


class CompanyCreate(BaseModel):
    name: str
    address: str
    phone: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int]

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

    class Config:
        orm_mode = True
        

        


class UserCreateByAdmin(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?\d{9,15}$")
    password: str = Field(..., min_length=6)
    role: RoleEnum

class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str]
    role: RoleEnum
    company_id: Optional[int]

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    role: RoleEnum

    class Config:
        from_attributes = True 

