"""ISO certification tables

Revision ID: 2024_03_iso_certification
Revises: d98dd8ec85a3
Create Date: 2024-03-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_03_iso_certification'
down_revision = 'd98dd8ec85a3'
branch_labels = None
depends_on = None


def upgrade():
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('industry', sa.String(), nullable=False),
        sa.Column('registration_number', sa.String(), nullable=False),
        sa.Column('employees', sa.Integer(), nullable=False),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('logo', sa.String(), nullable=True),
    )

    # Create QMS types table
    op.create_table(
        'qms_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.UniqueConstraint('name', name='uq_qms_types_name')
    )

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('qms_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('form_data', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['qms_type_id'], ['qms_types.id'], ondelete='CASCADE')
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('qms_type_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['qms_type_id'], ['qms_types.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('ix_companies_email', 'companies', ['email'])
    op.create_index('ix_companies_registration_number', 'companies', ['registration_number'])
    op.create_index('ix_applications_company_id', 'applications', ['company_id'])
    op.create_index('ix_applications_qms_type_id', 'applications', ['qms_type_id'])
    op.create_index('ix_documents_qms_type_id', 'documents', ['qms_type_id'])

    # Add trigger for updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_applications_updated_at
            BEFORE UPDATE ON applications
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade():
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS update_applications_updated_at ON applications")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")

    # Drop tables
    op.drop_table('documents')
    op.drop_table('applications')
    op.drop_table('qms_types')
    op.drop_table('companies') 