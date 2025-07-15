from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import List, Dict
from .models import RoleEnum, DepartmentUser, User
from sqlalchemy.orm import Session
from .database import get_db
from .auth import get_current_user

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {"tasks": [], "private": {}, "dept": {}}

    async def connect_tasks(self, ws: WebSocket):
        await ws.accept()
        self.active["tasks"].append(ws)

    async def broadcast_tasks(self, message: str):
        for ws in self.active["tasks"]:
            await ws.send_text(message)

    async def connect_private(self, ws: WebSocket, room_id: str):
        await ws.accept()
        self.active["private"].setdefault(room_id, []).append(ws)

    async def send_private(self, room_id: str, message: str):
        for ws in self.active["private"].get(room_id, []):
            await ws.send_text(message)

    async def connect_dept(self, ws: WebSocket, dept_id: int):
        await ws.accept()
        key = f"dept_{dept_id}"
        self.active["dept"].setdefault(key, []).append(ws)

    async def broadcast_dept(self, dept_id: int, message: str):
        key = f"dept_{dept_id}"
        for ws in self.active["dept"].get(key, []):
            await ws.send_text(message)

    def disconnect(self, ws: WebSocket):
        for conns in self.active.values():
            if isinstance(conns, dict):
                for lst in conns.values():
                    if ws in lst: lst.remove(ws)
            else:
                if ws in conns: conns.remove(ws)

manager = ConnectionManager()

# Role-based dependency
def require_role(*roles: RoleEnum):
    def dep(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges")
        return user
    return dep