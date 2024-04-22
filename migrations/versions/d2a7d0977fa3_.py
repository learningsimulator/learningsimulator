"""empty message

Revision ID: d2a7d0977fa3
Revises: 5eef3e5209fa
Create Date: 2023-08-07 23:06:04.693126

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd2a7d0977fa3'
down_revision = '5eef3e5209fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=True))
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=300),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.String(length=300),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)
        batch_op.drop_column('is_admin')

    # ### end Alembic commands ###