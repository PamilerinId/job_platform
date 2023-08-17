"""files table

Revision ID: d31e4230608b
Revises: 9d6304faaaa3
Create Date: 2023-08-17 22:22:24.163611

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd31e4230608b'
down_revision = '9d6304faaaa3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('files', 'type',
               existing_type=postgresql.ENUM('PROFILE_PHOTO', 'RESUME', 'COVER_LETTER', 'VIDEO', name='filetype'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('files',
    # sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    # sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    # sa.Column('url', sa.VARCHAR(), autoincrement=False, nullable=False),
    # sa.Column('type', postgresql.ENUM('RESUME', 'COVER_LETTER', 'VIDEO', name='filetype'), autoincrement=False, nullable=True),
    # sa.Column('owner_id', sa.UUID(), autoincrement=False, nullable=True),
    # sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    # sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    # sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='files_owner_id_fkey'),
    # sa.PrimaryKeyConstraint('id', name='files_pkey'),
    # sa.UniqueConstraint('url', name='files_url_key')
    # )
    pass
    # ### end Alembic commands ###
