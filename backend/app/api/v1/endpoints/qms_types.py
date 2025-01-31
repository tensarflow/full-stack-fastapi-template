from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.post("/", response_model=schemas.QMSType)
def create_qms_type(
    *,
    db: Session = Depends(deps.get_db),
    qms_type_in: schemas.QMSTypeCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Create new QMS type."""
    qms_type = crud.create_qms_type(db=db, qms_type_data=qms_type_in.model_dump())
    return qms_type

@router.get("/", response_model=schemas.QMSTypeList)
def read_qms_types(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve QMS types."""
    qms_types = crud.get_qms_types(db=db, skip=skip, limit=limit)
    total = len(qms_types)
    return {"items": qms_types, "total": total}

@router.put("/{qms_type_id}", response_model=schemas.QMSType)
def update_qms_type(
    *,
    db: Session = Depends(deps.get_db),
    qms_type_id: UUID,
    qms_type_in: schemas.QMSTypeUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Update QMS type."""
    qms_type = crud.get_qms_type(db=db, qms_type_id=qms_type_id)
    if not qms_type:
        raise HTTPException(status_code=404, detail="QMS type not found")
    qms_type = crud.update_qms_type(
        db=db, qms_type_id=qms_type_id, qms_type_data=qms_type_in.model_dump()
    )
    return qms_type

@router.delete("/{qms_type_id}")
def delete_qms_type(
    *,
    db: Session = Depends(deps.get_db),
    qms_type_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete QMS type."""
    qms_type = crud.get_qms_type(db=db, qms_type_id=qms_type_id)
    if not qms_type:
        raise HTTPException(status_code=404, detail="QMS type not found")
    crud.delete_qms_type(db=db, qms_type_id=qms_type_id)
    return {"message": "QMS type deleted successfully"} 