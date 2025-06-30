
from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# create user
def create_user(db: Session, user: schemas.UserCreate, role: models.RoleEnum = models.RoleEnum.employee):
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
    # assign company to admin
    admin_user.company_id = db_company.id
    admin_user.role = models.RoleEnum.company_admin
    db.commit()
    db.refresh(admin_user)
    return db_company