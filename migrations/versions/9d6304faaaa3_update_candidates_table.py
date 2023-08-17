"""update candidates table

Revision ID: 9d6304faaaa3
Revises: 94d88b024507
Create Date: 2023-08-17 22:17:07.765913

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9d6304faaaa3'
down_revision = '94d88b024507'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('files')
    op.alter_column('applications', 'comment',
               existing_type=sa.TEXT(),
               nullable=True)
    op.add_column('candidate_profiles', sa.Column('currency', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('candidate_profiles', 'currency')
    op.alter_column('applications', 'comment',
               existing_type=sa.TEXT(),
               nullable=False)
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
    # ### end Alembic commands ###
