from pydantic import BaseModel, EmailStr
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

class CompanyCreate(BaseModel):
    name: str
    address: str
    phone: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int]
    