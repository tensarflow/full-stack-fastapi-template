from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.api import deps
from app.core.config import settings
import os

# Create upload directory if it doesn't exist
os.makedirs(f"{settings.UPLOADS_DIR}/company_logos", exist_ok=True)

router = APIRouter()

@router.post("/", response_model=schemas.Company)
def create_company(
    *,
    db: Session = Depends(deps.get_db),
    company_in: schemas.CompanyCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new company.
    """
    company = crud.create_company(db=db, company_data=company_in.model_dump())
    return company

@router.get("/", response_model=schemas.CompanyList)
def read_companies(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve companies.
    """
    companies = crud.get_companies(db=db, skip=skip, limit=limit)
    total = len(companies)  # In production, you'd want to do a COUNT query
    return {"items": companies, "total": total}

@router.get("/{company_id}", response_model=schemas.Company)
def read_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get company by ID.
    """
    company = crud.get_company(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/{company_id}", response_model=schemas.Company)
def update_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    company_in: schemas.CompanyUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update company.
    """
    company = crud.get_company(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company = crud.update_company(
        db=db, company_id=company_id, company_data=company_in.model_dump()
    )
    return company

@router.delete("/{company_id}")
def delete_company(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete company.
    """
    company = crud.get_company(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    crud.delete_company(db=db, company_id=company_id)
    return {"message": "Company deleted successfully"}

@router.post("/{company_id}/logo")
async def upload_company_logo(
    *,
    db: Session = Depends(deps.get_db),
    company_id: UUID,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload company logo.
    """
    company = crud.get_company(db=db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Save file and update company logo path
    file_path = f"uploads/company_logos/{company_id}_{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(await file.read())
    
    company = crud.update_company(
        db=db, 
        company_id=company_id, 
        company_data={"logo": file_path}
    )
    return {"message": "Logo uploaded successfully", "file_path": file_path} 