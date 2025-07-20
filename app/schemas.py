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


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: Optional[int]

        
class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[RoleEnum] = None

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
        from_attributes = True

class CompanyCreate(BaseModel):
    name: str
    address: str
    phone: str

class CompanyRead(BaseModel):
    id: int
    name: str
    address: str
    phone: str

    class Config:
        from_attributes = True

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: int
    
class DepartmentRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    manager_id: Optional[int] = None
    users: list[UserRead] = []
    class Config:
        from_attributes = True

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[int] = None

class DepartmentDelete(BaseModel):
    id: int
    
class DepartmentUserCreate(BaseModel):
    user_id: int
    department_id: int

class DepartmentUserRead(BaseModel):
    id: int
    user_id: int
    department_id: int
    user: UserRead
    created_at: str
    class Config:
        from_attributes = True

class DepartmentUserUpdate(BaseModel):
    user_id: Optional[int] = None
    department_id: Optional[int] = None

class DepartmentUserDelete(BaseModel):
    id: int
    
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "to_do"
    assigned_to: int
    department_id: int
    deadline: Optional[str] = None
    
class TaskRead(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: UserRead
    department_id: DepartmentRead
    deadline: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None
    department_id: Optional[int] = None
    completed_at: Optional[str] = None
    
class TaskDelete(BaseModel):
    id: int

class SubtaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "to_do"
    task_id: int


class SubtaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str
    task_id: int
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    class Config:
        from_attributes = True


class SubtaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    task_id: Optional[int] = None

class SubtaskDelete(BaseModel):
    id: int
    
