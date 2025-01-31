from docxtpl import DocxTemplate
from app.models import Application, Company

def generate_document(template_path: str, output_path: str, application: Application, company: Company) -> None:
    """Generate document from template."""
    doc = DocxTemplate(template_path)
    
    # Prepare context with all required data
    context = {
        "company_name": company.name,
        "company_address": company.address,
        "contact_person": company.contact_person,
        "contact_email": company.email,
        "contact_phone": company.phone,
        "industry": company.industry,
        "registration_number": company.registration_number,
        "employees": company.employees,
        "website": company.website,
        **application.form_data  # Include all form data
    }
    
    # Render and save document
    doc.render(context)
    doc.save(output_path) 