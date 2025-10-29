"""add_companies_table

Revision ID: 997f715e10a5
Revises: 5570a397f78d
Create Date: 2025-10-28 23:03:26.588649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '997f715e10a5'
down_revision = '5570a397f78d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=True)
    
    # Add company_id to reviews_feedback and create foreign key
    op.add_column('reviews_feedback', sa.Column('company_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_reviews_company', 'reviews_feedback', 'companies', ['company_id'], ['id'])
    op.create_index(op.f('ix_reviews_feedback_company_id'), 'reviews_feedback', ['company_id'], unique=False)
    
    # Migrate existing company names to companies table and update foreign keys
    # This will be done in a data migration script


def downgrade() -> None:
    op.drop_index(op.f('ix_reviews_feedback_company_id'), table_name='reviews_feedback')
    op.drop_constraint('fk_reviews_company', 'reviews_feedback', type_='foreignkey')
    op.drop_column('reviews_feedback', 'company_id')
    
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_table('companies')
