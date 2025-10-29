"""add_dataset_tables

Revision ID: 5570a397f78d
Revises: 48a924ddffc1
Create Date: 2025-10-28 22:57:37.462026

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5570a397f78d'
down_revision = '48a924ddffc1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_datasets table
    op.create_table(
        'user_datasets',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('column_metadata', sa.JSON(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_name'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )
    op.create_index(op.f('ix_user_datasets_user_id'), 'user_datasets', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_datasets_table_name'), 'user_datasets', ['table_name'], unique=False)

    # Create platform_datasets table
    op.create_table(
        'platform_datasets',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('table_name', sa.String(), nullable=False),
        sa.Column('collection_name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('data_category', sa.String(), nullable=True),
        sa.Column('field_descriptions', sa.JSON(), nullable=True),
        sa.Column('key_fields', sa.JSON(), nullable=True),
        sa.Column('embedding_fields', sa.JSON(), nullable=True),
        sa.Column('primary_text_field', sa.String(), nullable=True),
        sa.Column('combined_text_fields', sa.JSON(), nullable=True),
        sa.Column('estimated_use_cases', sa.JSON(), nullable=True),
        sa.Column('potential_joins', sa.JSON(), nullable=True),
        sa.Column('data_quality_notes', sa.Text(), nullable=True),
        sa.Column('row_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('table_name')
    )
    op.create_index(op.f('ix_platform_datasets_table_name'), 'platform_datasets', ['table_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_platform_datasets_table_name'), table_name='platform_datasets')
    op.drop_table('platform_datasets')
    
    op.drop_index(op.f('ix_user_datasets_table_name'), table_name='user_datasets')
    op.drop_index(op.f('ix_user_datasets_user_id'), table_name='user_datasets')
    op.drop_table('user_datasets')
