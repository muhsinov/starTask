from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import DepartmentUserCreate, DepartmentUserRead, DepartmentUserUpdate
from ..crud import create_department_user,update_department_user, delete_department_user, get_department_users
from ..database import get_db
from ..utils import require_role
from ..models import RoleEnum, DepartmentUser, Department
from ..auth import get_current_user
from typing import List

router = APIRouter(prefix="/department_users", tags=["department_users"])

@router.post("/", response_model=DepartmentUserRead)
def create(dept_user_in: DepartmentUserCreate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    department = db.query(Department).filter(dept_user_in.department_id == Department.id).first()
    if user.role != RoleEnum.company_admin and user.id != department.manager_id:
        raise HTTPException(status_code=403, detail="Siz faqat o'z bo'limingiz uchun foydalanuvchilarni qo'shishingiz mumkin")
    if db.query(DepartmentUser).filter(DepartmentUser.user_id == dept_user_in.user_id, DepartmentUser.department_id == dept_user_in.department_id).first():
        raise HTTPException(status_code=409, detail="Foydalanuvchi ushbu bo'limda allaqachon mavjud")
    return create_department_user(db, dept_user_in)

@router.get("/all/{department_id}", response_model=List[DepartmentUserRead])
def list_all(department_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.id == department_id).first()
    if user.role != RoleEnum.company_admin and user.id != department.manager_id and user.department_users != department_id:
        raise HTTPException(status_code=403, detail="Siz faqat o'z bo'limingiz foydalanuvchilarini ko'rishingiz mumkin")
    if not department:
        raise HTTPException(status_code=404, detail="Department topilmadi")
    return get_department_users(db, department_id)

@router.put("/{dept_user_id}", response_model=DepartmentUserRead)
def update(dept_user_id: int, dept_user_in: DepartmentUserUpdate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.id == dept_user_in.department_id).first()
    if user.role != RoleEnum.company_admin and user.id != department.manager_id:
        raise HTTPException(status_code=403, detail="Siz faqat o'z bo'limingiz foydalanuvchilarini yangilashingiz mumkin")
    if not db.query(DepartmentUser).get(dept_user_id):
        raise HTTPException(status_code=404, detail="Department user topilmadi")
    return update_department_user(db, dept_user_id, dept_user_in)

@router.delete("/{dept_user_id}")
def delete(dept_user_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.query(DepartmentUser).get(dept_user_id):
        raise HTTPException(status_code=404, detail="Department user topilmadi")
    if user.role != RoleEnum.company_admin and user.id != db.query(DepartmentUser).get(dept_user_id).department.manager_id:
        raise HTTPException(status_code=403, detail="Siz faqat o'z bo'limingiz foydalanuvchilarini o'chirishingiz mumkin")
    delete_department_user(db, dept_user_id)
    return {"detail": "Department user o'chirildi"}