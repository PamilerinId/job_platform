"""update answers

Revision ID: bc9c221f69ab
Revises: a97a05690055
Create Date: 2023-11-03 14:49:29.322572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc9c221f69ab'
down_revision = 'a97a05690055'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('assessments', 'name', unique=True, nullable=False)


def downgrade() -> None:
    pass
