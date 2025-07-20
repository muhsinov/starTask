from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import event
from datetime import datetime
import enum




class RoleEnum(str, enum.Enum):
    company_admin = "company_admin"
    department_manager = "department_manager"
    employee = "employee"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.company_admin)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), 
        nullable=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),         
        nullable=True
    )
    
    company = relationship("Company", back_populates="users")
    department_users = relationship("DepartmentUser", back_populates="user")
    managed_departments = relationship("Department", back_populates="manager")
    tasks = relationship("Task", back_populates="assigned_to", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    users = relationship("User", back_populates="company")
    
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager = relationship("User", back_populates="managed_departments")
    department_users = relationship("DepartmentUser", back_populates="department")
    
class DepartmentUser(Base):
    __tablename__ = "department_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    
    user = relationship("User", back_populates="department_users")
    department = relationship("Department", back_populates="department_users")
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),         
        nullable=False
    )

class TaskStatusEnum(str, enum.Enum):
    to_do = "to_do"
    doing = "doing"
    done = "done"
    
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.to_do)
    deadline = Column(DateTime(timezone=True), nullable=True)
    
    assigned_to = relationship("User", back_populates="tasks")
    department = relationship("Department")
    subtasks = relationship("Subtask", back_populates="task", cascade="all, delete-orphan")
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),         
        nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
@event.listens_for(Task, 'before_update')
def set_task_completed_at(mapper, connection, target):
    if target.status == TaskStatusEnum.done and target.completed_at is None:
        target.completed_at = datetime.utcnow()
    
    
class Subtask(Base):
    __tablename__ = "subtasks"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.to_do)
    
    task = relationship("Task", back_populates="subtasks")
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),         
        nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)


@event.listens_for(Subtask, 'before_update')
def set_subtask_completed_at(mapper, connection, target):
    if target.status == TaskStatusEnum.done and target.completed_at is None:
        target.completed_at = datetime.utcnow()

class ChatType(str, enum.Enum):
    private = "private"
    department = "department"

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    chat_type = Column(Enum(ChatType), nullable=False)
    room = Column(String, nullable=False, index=True)  # room_id for private or dept_id
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
