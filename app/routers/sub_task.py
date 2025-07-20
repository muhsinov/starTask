from fastapi import APIRouter, Depends, WebSocket, HTTPException
from sqlalchemy.orm import Session
from ..schemas import SubtaskCreate, SubtaskRead, SubtaskUpdate
from app.crud import create_subtask, update_subtask, read_subtasks, delete_subtask
from ..database import get_db
from ..utils import require_role
from ..models import RoleEnum, Subtask
from ..auth import get_current_user
from typing import List

def check_subtask_exists(db: Session, subtask_id: int):
    if db.query(Subtask).filter(Subtask.id == subtask_id).first() is not None:
        return HTTPException(status_code=404, detail="Subtask not found")
    

router = APIRouter(prefix="/subtasks", tags=["subtasks"])

@router.post("/", response_model=SubtaskRead, dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def create(subtask_in: SubtaskCreate, db: Session = Depends(get_db)):
    return create_subtask(db, subtask_in)

@router.get("/{task_id}", response_model=List[SubtaskRead])
def list_all(task_id: int, db: Session = Depends(get_db)):
    return read_subtasks(db, task_id)
    
@router.put("/{subtask_id}", response_model=SubtaskUpdate, dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def update(subtask_id: int, subtask_in: SubtaskUpdate, db: Session = Depends(get_db)):
    check_subtask_exists(db, subtask_id)
    return update_subtask(db, subtask_id, subtask_in)

@router.delete("/{subtask_id}", dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def delete(subtask_id: int, db: Session = Depends(get_db)):
    check_subtask_exists(db, subtask_id)
    return delete_subtask(db, subtask_id)