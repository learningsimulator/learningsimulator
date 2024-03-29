"""Fixing typo in previous migration

Revision ID: 5cb6c1b817bf
Revises: 4f6b84a12ec0
Create Date: 2023-03-17 17:51:58.947680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cb6c1b817bf'
down_revision = '4f6b84a12ec0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress2', sa.Double(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.drop_column('progress2')

    # ### end Alembic commands ###
