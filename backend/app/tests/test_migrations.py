from sqlalchemy import text
from sqlalchemy.orm import Session

def test_migrations(db: Session) -> None:
    """Test that all migrations run successfully."""
    # Test companies table
    result = db.execute(text("SELECT * FROM companies LIMIT 1"))
    assert result.keys() == [
        'id', 'name', 'address', 'contact_person', 'email', 'phone',
        'industry', 'registration_number', 'employees', 'website', 'logo'
    ]

    # Test QMS types table
    result = db.execute(text("SELECT * FROM qms_types LIMIT 1"))
    assert result.keys() == ['id', 'name']

    # Test applications table
    result = db.execute(text("SELECT * FROM applications LIMIT 1"))
    assert result.keys() == [
        'id', 'company_id', 'qms_type_id', 'created_at', 'updated_at', 'form_data'
    ]

    # Test documents table
    result = db.execute(text("SELECT * FROM documents LIMIT 1"))
    assert result.keys() == ['id', 'title', 'qms_type_id', 'file_path']

    # Test updated_at trigger
    db.execute(text("""
        INSERT INTO companies (id, name, address, contact_person, email, phone, 
                             industry, registration_number, employees)
        VALUES (
            '123e4567-e89b-12d3-a456-426614174000',
            'Test Company',
            'Test Address',
            'John Doe',
            'test@example.com',
            '1234567890',
            'Technology',
            'REG123',
            100
        )
    """))

    db.execute(text("""
        INSERT INTO qms_types (id, name)
        VALUES ('123e4567-e89b-12d3-a456-426614174001', 'ISO 9001')
    """))

    db.execute(text("""
        INSERT INTO applications (
            id, company_id, qms_type_id, form_data
        ) VALUES (
            '123e4567-e89b-12d3-a456-426614174002',
            '123e4567-e89b-12d3-a456-426614174000',
            '123e4567-e89b-12d3-a456-426614174001',
            '{"field1": "value1"}'::jsonb
        )
    """))

    # Update application
    db.execute(text("""
        UPDATE applications 
        SET form_data = '{"field1": "value2"}'::jsonb
        WHERE id = '123e4567-e89b-12d3-a456-426614174002'
    """))

    # Check if updated_at was changed
    result = db.execute(text("""
        SELECT created_at != updated_at as was_updated
        FROM applications
        WHERE id = '123e4567-e89b-12d3-a456-426614174002'
    """)).first()

    assert result.was_updated is True

    db.rollback() 