"""Change default plot size

Revision ID: 70d012ea0252
Revises: 408bda874f27
Create Date: 2023-09-23 16:56:18.303227

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '70d012ea0252'
down_revision = '408bda874f27'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('email',
               existing_type=mysql.VARCHAR(length=150),
               type_=sa.String(length=50),
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
        batch_op.alter_column('email',
               existing_type=sa.String(length=50),
               type_=mysql.VARCHAR(length=150),
               existing_nullable=True)

    # ### end Alembic commands ###
