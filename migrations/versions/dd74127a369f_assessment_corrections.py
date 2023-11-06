"""assessment corrections

Revision ID: dd74127a369f
Revises: d31e4230608b
Create Date: 2023-11-03 11:45:36.222423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd74127a369f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('answers', sa.Column('is_correct', sa.Boolean(), server_default='False', nullable=True))
    op.drop_column('questions', 'answer_ids')


def downgrade() -> None:
    pass