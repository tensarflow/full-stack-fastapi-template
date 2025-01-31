from fastapi import APIRouter
from app.api.v1.endpoints import companies, qms_types, documents, applications

api_router = APIRouter()
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(qms_types.router, prefix="/qms-types", tags=["qms-types"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"]) 