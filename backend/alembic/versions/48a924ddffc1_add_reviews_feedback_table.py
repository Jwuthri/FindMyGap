"""add_reviews_feedback_table

Revision ID: 48a924ddffc1
Revises: f87c0a5c0ce6
Create Date: 2025-10-28 22:50:51.625060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48a924ddffc1'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reviews_feedback',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('author', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_feedback_company'), 'reviews_feedback', ['company'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_reviews_feedback_company'), table_name='reviews_feedback')
    op.drop_table('reviews_feedback')
