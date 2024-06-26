"""empty message

Revision ID: df8ef45da2d4
Revises: 65d4702dabec
Create Date: 2023-09-16 21:37:05.516684

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'df8ef45da2d4'
down_revision = '65d4702dabec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('db_script', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_archived', sa.Boolean(), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=50),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=mysql.VARCHAR(length=300),
               type_=sa.String(length=100),
               existing_nullable=True)
        batch_op.alter_column('username',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=100),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('username',
               existing_type=sa.String(length=100),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)
        batch_op.alter_column('password',
               existing_type=sa.String(length=100),
               type_=mysql.VARCHAR(length=300),
               existing_nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)

    with op.batch_alter_table('db_script', schema=None) as batch_op:
        batch_op.drop_column('is_archived')

    # ### end Alembic commands ###
