from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas import SubtaskCreate, SubtaskRead, SubtaskUpdate
from app.crud import create_subtask, update_subtask, read_subtasks, delete_subtask
from ..database import get_db
from ..utils import require_role
from ..models import RoleEnum, Subtask
from ..auth import get_current_user
from typing import List

def check_subtask_exists(db: Session, subtask_id: int):
    return db.query(Subtask).filter(Subtask.id == subtask_id).first() is not None
        
    

router = APIRouter(prefix="/subtasks", tags=["subtasks"])

@router.post("/", response_model=SubtaskRead)
def create(subtask_in: SubtaskCreate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.id != subtask_in.task.department.manager_id and user.role != RoleEnum.company_admin:
        raise HTTPException(status_code=403, detail="You can only create subtasks for your own tasks")
    return create_subtask(db, subtask_in)

@router.get("/{task_id}", response_model=List[SubtaskRead])
def list_all(task_id: int, db: Session = Depends(get_db)):
    if db.query(Subtask).filter(Subtask.task_id == task_id).count() == 0:
        raise HTTPException(status_code=404, detail="No subtasks found for this task")
    return read_subtasks(db, task_id)
    
@router.put("/{subtask_id}", response_model=SubtaskUpdate)
def update(subtask_id: int, subtask_in: SubtaskUpdate, user = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.id != subtask_in.task.department.manager_id and user.role != RoleEnum.company_admin:
        raise HTTPException(status_code=403, detail="You can only update subtasks for your own tasks")
    if not check_subtask_exists(db, subtask_id):
        raise HTTPException(status_code=404, detail="Subtask not found")
    return update_subtask(db, subtask_id, subtask_in)

@router.delete("/{subtask_id}")
def delete(subtask_id: int, user = Depends(get_current_user), db: Session = Depends(get_db)):
    subtask_in = db.query(Subtask).filter(Subtask.id == subtask_id).first()
    if user.id != subtask_in.task.department.manager_id and user.role != RoleEnum.company_admin:
        raise HTTPException(status_code=403, detail="You can only delete subtasks for your own tasks")
    if not check_subtask_exists(db, subtask_id):
        raise HTTPException(status_code=404, detail="Subtask not found")
    return delete_subtask(db, subtask_id)