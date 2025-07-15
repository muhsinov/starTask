from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Message, ChatType, RoleEnum
from ..utils import manager, require_role
from ..auth import get_current_user


router = APIRouter(prefix="/chat", tags=["chat"])

@router.websocket("/private/{room_id}")
async def ws_private(ws: WebSocket, room_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    await manager.connect_private(ws, room_id)
    try:
        while True:
            text = await ws.receive_text()
            msg = Message(content=text, chat_type=ChatType.private, room=room_id)
            db.add(msg); db.commit(); db.refresh(msg)
            await manager.send_private(room_id, text)
    finally:
        manager.disconnect(ws)

@router.websocket("/department/{dept_id}")
async def ws_dept(ws: WebSocket, dept_id: int, db: Session = Depends(get_db), user=Depends(require_role(RoleEnum.company_admin, RoleEnum.department_manager, RoleEnum.employee))):
    await manager.connect_dept(ws, dept_id)
    try:
        while True:
            text = await ws.receive_text()
            msg = Message(content=text, chat_type=ChatType.department, room=str(dept_id))
            db.add(msg); db.commit(); db.refresh(msg)
            await manager.broadcast_dept(dept_id, text)
    finally:
        manager.disconnect(ws)