import uuid
from typing import Any
from sqlalchemy.orm import Session
from . import models
from datetime import datetime

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Company CRUD operations
def create_company(db: Session, company_data: dict):
    db_company = models.Company(**company_data)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def get_company(db: Session, company_id: uuid.UUID):
    return db.query(models.Company).filter(models.Company.id == company_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Company).offset(skip).limit(limit).all()

def update_company(db: Session, company_id: uuid.UUID, company_data: dict):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company:
        for key, value in company_data.items():
            setattr(db_company, key, value)
        db.commit()
        db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: uuid.UUID):
    db_company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if db_company:
        db.delete(db_company)
        db.commit()
        return True
    return False

# QMS Type CRUD operations
def create_qms_type(db: Session, qms_type_data: dict):
    db_qms_type = models.QMSType(**qms_type_data)
    db.add(db_qms_type)
    db.commit()
    db.refresh(db_qms_type)
    return db_qms_type

def get_qms_type(db: Session, qms_type_id: uuid.UUID):
    return db.query(models.QMSType).filter(models.QMSType.id == qms_type_id).first()

def get_qms_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.QMSType).offset(skip).limit(limit).all()

def update_qms_type(db: Session, qms_type_id: uuid.UUID, qms_type_data: dict):
    db_qms_type = db.query(models.QMSType).filter(models.QMSType.id == qms_type_id).first()
    if db_qms_type:
        for key, value in qms_type_data.items():
            setattr(db_qms_type, key, value)
        db.commit()
        db.refresh(db_qms_type)
    return db_qms_type

def delete_qms_type(db: Session, qms_type_id: uuid.UUID):
    db_qms_type = db.query(models.QMSType).filter(models.QMSType.id == qms_type_id).first()
    if db_qms_type:
        db.delete(db_qms_type)
        db.commit()
        return True
    return False

# Application CRUD operations
def create_application(db: Session, application_data: dict):
    db_application = models.Application(**application_data)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def get_application(db: Session, application_id: uuid.UUID):
    return db.query(models.Application).filter(models.Application.id == application_id).first()

def get_applications(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Application).offset(skip).limit(limit).all()

def update_application(db: Session, application_id: uuid.UUID, application_data: dict):
    db_application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if db_application:
        application_data["updated_at"] = datetime.utcnow()
        for key, value in application_data.items():
            setattr(db_application, key, value)
        db.commit()
        db.refresh(db_application)
    return db_application

# Document CRUD operations
def create_document(db: Session, document_data: dict):
    db_document = models.Document(**document_data)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: uuid.UUID):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents_by_qms_type(db: Session, qms_type_id: uuid.UUID):
    return db.query(models.Document).filter(models.Document.qms_type_id == qms_type_id).all()

def delete_document(db: Session, document_id: uuid.UUID):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document:
        db.delete(db_document)
        db.commit()
        return True
    return False
