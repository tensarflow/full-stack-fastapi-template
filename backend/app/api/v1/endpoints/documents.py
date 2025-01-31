from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
import os

# Create upload directory if it doesn't exist
os.makedirs(f"{settings.UPLOADS_DIR}/qms_documents", exist_ok=True)

router = APIRouter()

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    *,
    db: Session = Depends(deps.get_db),
    qms_type_id: UUID,
    title: str,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Upload document template."""
    # Verify QMS type exists
    qms_type = crud.get_qms_type(db=db, qms_type_id=qms_type_id)
    if not qms_type:
        raise HTTPException(status_code=404, detail="QMS type not found")
    
    # Save file
    file_path = f"{settings.UPLOADS_DIR}/qms_documents/{qms_type_id}_{file.filename}"
    with open(file_path, "wb+") as file_object:
        file_object.write(await file.read())
    
    # Create document record
    document_data = {
        "title": title,
        "qms_type_id": qms_type_id,
        "file_path": file_path
    }
    document = crud.create_document(db=db, document_data=document_data)
    return document

@router.get("/{qms_type_id}", response_model=schemas.DocumentList)
def read_documents(
    *,
    db: Session = Depends(deps.get_db),
    qms_type_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Get all documents for a QMS type."""
    documents = crud.get_documents_by_qms_type(db=db, qms_type_id=qms_type_id)
    total = len(documents)
    return {"items": documents, "total": total}

@router.delete("/{document_id}")
def delete_document(
    *,
    db: Session = Depends(deps.get_db),
    document_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete document."""
    document = crud.get_document(db=db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    crud.delete_document(db=db, document_id=document_id)
    return {"message": "Document deleted successfully"} 