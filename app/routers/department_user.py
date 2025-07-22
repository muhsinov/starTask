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
def create(dept_user_in: DepartmentUserCreate, db: Session = Depends(get_db)):
    user = get_current_user()
    if user.role != RoleEnum.company_admin or user.id != dept_user_in.department.manager_id:
        raise HTTPException(status_code=403, detail="You can only create department users for your own department")
    return create_department_user(db, dept_user_in.user_id, dept_user_in.department_id)

@router.get("/all/{department_id}", response_model=List[DepartmentUserRead])
def list_all(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).get(Department.id == department_id, None)
    user = get_current_user()
    if user.role != RoleEnum.company_admin and user.id != department.manager_id or user.department_id != department_id:
        raise HTTPException(status_code=403, detail="You can only view users for your own department")
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return get_department_users(db, department_id)

@router.put("/{dept_user_id}", response_model=DepartmentUserRead)
def update(dept_user_id: int, dept_user_in: DepartmentUserUpdate, db: Session = Depends(get_db)):
    user = get_current_user()
    if user.role != RoleEnum.company_admin or user.id != dept_user_in.department.manager_id:
        raise HTTPException(status_code=403, detail="You can only update department users for your own department")
    if not db.query(DepartmentUser).get(dept_user_id):
        raise HTTPException(status_code=404, detail="Department user not found")
    return update_department_user(db, dept_user_id, dept_user_in)

@router.delete("/{dept_user_id}")
def delete(dept_user_id: int, db: Session = Depends(get_db)):
    user = get_current_user()
    if not db.query(DepartmentUser).get(dept_user_id):
        raise HTTPException(status_code=404, detail="Department user not found")
    if user.role != RoleEnum.company_admin or user.id != db.query(DepartmentUser).get(dept_user_id).department.manager_id:
        raise HTTPException(status_code=403, detail="You can only delete department users for your own department")
    return delete_department_user(db, dept_user_id)