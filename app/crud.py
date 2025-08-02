from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
from passlib.context import CryptContext
from typing import List
from sqlalchemy.orm import Session
from .models import Department, Task, Subtask, Message, DepartmentUser, User
from .schemas import (DepartmentCreate, DepartmentUpdate, DepartmentUserCreate, TaskCreate, TaskUpdate, SubtaskCreate, SubtaskUpdate)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate, role: models.RoleEnum = models.RoleEnum.company_admin):
    hashed_pw = get_password_hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_pw,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# get user by phone
def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()


# create company
def create_company(db: Session, company: schemas.CompanyCreate, admin_user: models.User):
    db_company = models.Company(
        name=company.name,
        address=company.address,
        phone=company.phone
    )
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    admin_user.company_id = db_company.id
    admin_user.role = models.RoleEnum.company_admin
    db.commit()
    db.refresh(admin_user)
    return db_company

def get_company_by_name(db: Session, name: str):
    return db.query(models.Company).filter(models.Company.name == name).first()



def create_user_for_company(db: Session, user_in: schemas.UserCreateByAdmin, company_id: int):
    hashed = get_password_hash(user_in.password)
    db_user = models.User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hashed,
        role=user_in.role,
        company_id=company_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ---Department---
def create_department(db: Session, dept_in: DepartmentCreate) -> Department:
    dept = Department(
        name=dept_in.name,
        description=dept_in.description,
        manager_id=dept_in.manager_id
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def get_departments(db: Session) -> List[Department]:
    return db.query(Department).all()


def update_department(db: Session, dept_id: int, dept_in: DepartmentUpdate) -> Department:
    dept = db.query(Department).get(dept_id)
    for key, value in dept_in.dict(exclude_unset=True).items():
        setattr(dept, key, value)
    db.commit()
    db.refresh(dept)
    return dept


def delete_department(db: Session, dept_id: int) -> None:
    db.query(Department).filter(Department.id == dept_id).delete()
    db.commit()
    
# --- DepartmentUser CRUD ---

def create_department_user(db: Session, dept_user_in: DepartmentUserCreate) -> DepartmentUser:
    department_user = DepartmentUser(department_id=dept_user_in.department_id,user_id=dept_user_in.user_id)
    db.add(department_user)
    db.commit()
    db.refresh(department_user)
    return department_user

def get_department_users(db: Session, department_id: int) -> List[DepartmentUser]:
    return db.query(DepartmentUser).filter(DepartmentUser.department_id == department_id).all()

def update_department_user(db: Session, department_user_id: int, du_in: DepartmentUser) -> DepartmentUser:
    department_user_id = db.query(DepartmentUser).get(department_user_id)
    for key, value in du_in.dict(exclude_unset=True).items():
        setattr(department_user_id, key, value)
    db.commit()
    db.refresh(department_user_id)
    return department_user_id

def delete_department_user(db: Session, department_user_id: int) -> None:
    db.query(DepartmentUser).filter(DepartmentUser.id == department_user_id).delete()
    db.commit()

# --- Task CRUD ---

def create_task(db: Session, t_in: TaskCreate) -> Task:
    task = Task(
        title=t_in.title,
        description=t_in.description if t_in.description else None,
        assigned_to_id=t_in.assigned_to if t_in.assigned_to else None,
        department_id=t_in.department_id if t_in.department_id else None,
        deadline=t_in.deadline if t_in.deadline else None,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def read_tasks(db: Session, department_id: int) -> List[models.Task]:
    return db.query(models.Task).filter(
            models.Task.department_id == department_id
    ).all()

def update_task(db: Session, task_id: int, t_in: TaskUpdate) -> Task:
    task = db.query(Task).get(task_id)
    for key, value in t_in.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task_id: int) -> None:
    db.query(Task).filter(Task.id == task_id).delete()
    db.commit()

# --- Subtask CRUD ---

def read_subtasks(db: Session, task_id: int) -> List[Subtask]:
    return db.query(Subtask).filter(Subtask.task_id == task_id).all()

def create_subtask(db: Session, s_in: SubtaskCreate) -> Subtask:
    sub = Subtask(
        title=s_in.title,
        description=s_in.description,
        task_id=s_in.task_id
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def update_subtask(db: Session, sub_id: int, s_in: SubtaskUpdate) -> Subtask:
    sub = db.query(Subtask).get(sub_id)
    for key, value in s_in.dict(exclude_unset=True).items():
        setattr(sub, key, value)
    db.commit()
    db.refresh(sub)
    return sub


def delete_subtask(db: Session, sub_id: int) -> None:
    db.query(Subtask).filter(Subtask.id == sub_id).delete()
    db.commit()

# --- Message CRUD (optional) ---
def create_message(db: Session, content: str, chat_type, room: str) -> Message:
    msg = Message(content=content, chat_type=chat_type, room=room)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def get_department_by_id(db: Session, dept_id: int) -> Department | None:
    return db.query(Department).filter(Department.id == dept_id).first()