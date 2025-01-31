from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils.document_generator import generate_document
import os

router = APIRouter()

@router.post("/", response_model=schemas.Application)
def create_application(
    *,
    db: Session = Depends(deps.get_db),
    application_in: schemas.ApplicationCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Create new application."""
    # Verify company and QMS type exist
    company = crud.get_company(db=db, company_id=application_in.company_id)
    qms_type = crud.get_qms_type(db=db, qms_type_id=application_in.qms_type_id)
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if not qms_type:
        raise HTTPException(status_code=404, detail="QMS type not found")
    
    application = crud.create_application(db=db, application_data=application_in.model_dump())
    return application

@router.get("/", response_model=schemas.ApplicationList)
def read_applications(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve applications."""
    applications = crud.get_applications(db=db, skip=skip, limit=limit)
    total = len(applications)
    return {"items": applications, "total": total}

@router.get("/{application_id}", response_model=schemas.Application)
def read_application(
    *,
    db: Session = Depends(deps.get_db),
    application_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get application by ID."""
    application = crud.get_application(db=db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application

@router.post("/{application_id}/generate-documents")
async def generate_documents(
    *,
    db: Session = Depends(deps.get_db),
    application_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Generate documents for application."""
    application = crud.get_application(db=db, application_id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Get all documents for this QMS type
    documents = crud.get_documents_by_qms_type(db=db, qms_type_id=application.qms_type_id)
    
    generated_files = []
    for document in documents:
        output_path = f"{settings.UPLOADS_DIR}/generated/{application_id}_{document.title}.docx"
        generate_document(
            template_path=document.file_path,
            output_path=output_path,
            application=application,
            company=application.company
        )
        generated_files.append({"title": document.title, "path": output_path})
    
    return {"message": "Documents generated successfully", "files": generated_files}

@router.get("/{application_id}/download/{document_id}")
async def download_document(
    *,
    db: Session = Depends(deps.get_db),
    application_id: UUID,
    document_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Download generated document."""
    document = crud.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    generated_path = f"{settings.UPLOADS_DIR}/generated/{application_id}_{document.title}.docx"
    if not os.path.exists(generated_path):
        raise HTTPException(status_code=404, detail="Generated document not found")
    
    return FileResponse(
        generated_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{document.title}.docx"
    ) 