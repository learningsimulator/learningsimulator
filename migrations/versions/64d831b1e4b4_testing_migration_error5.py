"""Testing migration error5.

Revision ID: 64d831b1e4b4
Revises: 9bf549ac28d9
Create Date: 2022-10-20 10:34:35.609179

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '64d831b1e4b4'
down_revision = '9bf549ac28d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'foo')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('foo', mysql.VARCHAR(length=3), nullable=True))
    # ### end Alembic commands ###