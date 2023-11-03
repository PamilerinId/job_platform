"""update answers

Revision ID: a97a05690055
Revises: dd74127a369f
Create Date: 2023-11-03 14:23:52.195354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a97a05690055'
down_revision = 'dd74127a369f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('assessments', 'slug', unique=False, nullable=True)


def downgrade() -> None:
    pass
