from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.orm import Session
from ..schemas import TaskCreate, TaskRead, TaskUpdate
from app.crud import create_task, update_task
from ..database import get_db
from ..utils import require_role, manager
from ..models import RoleEnum
from ..auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, dependencies=[Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager))])
def create(t_in: TaskCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # enforce dept_manager restrictions
    return broadcast_and_return(t_in, db)

async def broadcast_and_return(t_in, db):
    task = create_task(db, t_in)
    import json
    data = json.dumps({"event": "task_created", "id": task.id, "title": task.title})
    await manager.broadcast_tasks(data)
    return task
