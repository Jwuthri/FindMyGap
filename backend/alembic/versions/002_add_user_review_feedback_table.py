"""add_user_review_feedback_table

Revision ID: 002
Revises: 48a924ddffc1
Create Date: 2025-10-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '997f715e10a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user_review_feedback',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('is_owner', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('access_type', sa.String(50), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['review_id'], ['reviews_feedback.id'], ondelete='CASCADE')
    )
    
    # Create indexes for efficient lookups
    op.create_index(op.f('ix_user_review_feedback_user_id'), 'user_review_feedback', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_review_feedback_review_id'), 'user_review_feedback', ['review_id'], unique=False)
    
    # Create unique constraint to prevent duplicate user-review pairs
    op.create_index(
        'ix_user_review_feedback_user_review_unique',
        'user_review_feedback',
        ['user_id', 'review_id'],
        unique=True
    )


def downgrade() -> None:
    op.drop_index('ix_user_review_feedback_user_review_unique', table_name='user_review_feedback')
    op.drop_index(op.f('ix_user_review_feedback_review_id'), table_name='user_review_feedback')
    op.drop_index(op.f('ix_user_review_feedback_user_id'), table_name='user_review_feedback')
    op.drop_table('user_review_feedback')
