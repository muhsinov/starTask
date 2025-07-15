from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.crud import create_department, get_departments, update_department, delete_department, get_department_by_id
from ..database import get_db
from ..utils import require_role, manager
from ..models import RoleEnum
from typing import List
from ..auth import get_current_user
from ..models import User, DepartmentUser


router = APIRouter(prefix="/departments", tags=["departments"])

@router.post("/", response_model=DepartmentRead, dependencies=[Depends(require_role(RoleEnum.company_admin))])
async def create(dept_in: DepartmentCreate, db: Session = Depends(get_db)):
    dept = create_department(db, dept_in)
    import json
    # endpoin­timiz async, shuning uchun await ishlaydi
    await manager.broadcast_tasks(json.dumps({
        "event": "new_department",
        "id": dept.id,
        "name": dept.name
    }))
    return dept



@router.get("/", response_model=List[DepartmentRead])
def list_all(db: Session = Depends(get_db)):
    return get_departments(db)



@router.get("/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager, RoleEnum.employee))])
def get_department(dept_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dept = get_department_by_id(db, dept_id)
    if not dept:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    
    if current_user.role == RoleEnum.company_admin:
        return dept
    
    if current_user.role == RoleEnum.department_manager and dept.manager_id == current_user.id:
        return dept

    membership = (
        db.query(DepartmentUser)
          .filter(
              DepartmentUser.department_id == dept_id,
              DepartmentUser.user_id == current_user.id
          )
          .first()
    )
    if current_user.role == RoleEnum.employee and membership:
        return dept

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Sizda ushbu bo'limni ko'rish huquqi yo'q"
    )



@router.patch("/{dept_id}", response_model=DepartmentRead, dependencies=[Depends(require_role(RoleEnum.company_admin))])
def update(dept_id: int, dept_in: DepartmentUpdate, db: Session = Depends(get_db)):
    return update_department(db, dept_id, dept_in)



@router.delete("/{dept_id}", status_code=204, dependencies=[Depends(require_role(RoleEnum.company_admin))])
def delete(dept_id: int, db: Session = Depends(get_db)):
    delete_department(db, dept_id)
    return