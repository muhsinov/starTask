from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
import app.crud as crud
import app.auth as auth
from app.database import engine, Base, get_db
from fastapi.security import OAuth2PasswordRequestForm
from .models import RoleEnum

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Register user
@app.post("/auth/register", response_model=schemas.Token)
def register(
    user_in: schemas.UserCreateWithCompany,  # bu yangi schema bo'ladi
    db: Session = Depends(get_db)
):
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # 1. Avval foydalanuvchini company_admin sifatida yaratamiz
    user = crud.create_user(db, user_in, role=models.RoleEnum.company_admin)

    # 2. Endi shu user orqali kompaniya yaratiladi
    company_data = schemas.CompanyCreate(
        name=user_in.company_name,
        address=user_in.company_address,
        phone=user_in.company_phone
    )
    crud.create_company(db, company_data, user)

    # 3. Access token beriladi
    access_token = auth.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# Login user
@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


# Protected route example
@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# add a new user to the company by admin or department manager
@app.post(
    "/users/invite",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a new employee to your company",
)
def invite_user(
    user_in: schemas.UserCreateByAdmin,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role not in {RoleEnum.company_admin}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sizda bu amalni bajarish huquqi yo'q",
        )

    company_id = current_user.company_id
    if company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Siz hali kompaniya bilan bog'lanmagansiz",
        )

    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email avval qo‘shilgan",
        )
    if crud.get_user_by_phone(db, user_in.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu telefon raqam avval qo‘shilgan",
        )

    new_user = crud.create_user_for_company(db, user_in, company_id)
    return new_user

from typing import List


# employees list for company admin
@app.get("/users/", response_model=List[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != RoleEnum.company_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchilar ro'yxatini faqat kompaniya admini ko'ra oladi",
        )

    users = db.query(models.User).filter(
        models.User.company_id == current_user.company_id,
        models.User.id != current_user.id  # admin o'zini ko‘rmasligi uchun
    ).all()
    return users
