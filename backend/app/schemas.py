from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, HttpUrl, constr

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    address: str
    contact_person: str
    email: EmailStr
    phone: str
    industry: str
    registration_number: str
    employees: int
    website: Optional[HttpUrl] = None
    logo: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(CompanyBase):
    pass

class Company(CompanyBase):
    id: UUID
    
    class Config:
        from_attributes = True

# QMS Type Schemas
class QMSTypeBase(BaseModel):
    name: str

class QMSTypeCreate(QMSTypeBase):
    pass

class QMSTypeUpdate(QMSTypeBase):
    pass

class QMSType(QMSTypeBase):
    id: UUID
    
    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    title: str
    qms_type_id: UUID
    file_path: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: str

class Document(DocumentBase):
    id: UUID
    
    class Config:
        from_attributes = True

# Application Schemas
class ApplicationBase(BaseModel):
    company_id: UUID
    qms_type_id: UUID
    form_data: dict

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(ApplicationBase):
    pass

class Application(ApplicationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Response Models
class CompanyList(BaseModel):
    items: list[Company]
    total: int

class QMSTypeList(BaseModel):
    items: list[QMSType]
    total: int

class DocumentList(BaseModel):
    items: list[Document]
    total: int

class ApplicationList(BaseModel):
    items: list[Application]
    total: int 