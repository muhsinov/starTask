import json
from fastapi import APIRouter, Depends, WebSocket, HTTPException
from sqlalchemy.orm import Session
from ..schemas import TaskCreate, TaskRead, TaskUpdate
from app.crud import create_task, update_task, read_tasks, delete_task
from ..database import get_db
from ..utils import require_role, manager
from ..models import RoleEnum, Task
from ..auth import get_current_user

def check_task_exists(db: Session, task_id: int):
    if db.query(Task).filter(Task.id == task_id).first() is None:
        raise HTTPException(status_code=404, detail="Task not found")

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, dependencies=[Depends(require_role(RoleEnum.company_admin))])
def create(t_in: TaskCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_current_user()
    if user.role != RoleEnum.company_admin or user.id != t_in.department.manager_id:
        raise HTTPException(status_code=403, detail="You can only create tasks for your own department")
    return create_task(db, t_in)


@router.put("/{task_id}", response_model=TaskUpdate, dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def update(task_id: int, t_in: TaskUpdate, db: Session = Depends(get_db)):
    check_task_exists(db, task_id)
    return update_task(db, task_id, t_in)

@router.get("/",  response_model=list[TaskRead])
def list_all(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    user = current_user.id
    department = current_user.departemt_id
    print(f"User ID: {user}, Department ID: {department}")
    return read_tasks(db, user, department)


@router.delete("/{task_id}", dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def delete(task_id: int, db: Session = Depends(get_db)):
    check_task_exists(db, task_id)
    return delete_task(db, task_id)