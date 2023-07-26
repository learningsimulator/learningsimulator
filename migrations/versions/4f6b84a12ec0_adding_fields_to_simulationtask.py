"""Adding fields to SimulationTask

Revision ID: 4f6b84a12ec0
Revises: f98c730d6527
Create Date: 2023-03-17 17:48:01.338831

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4f6b84a12ec0'
down_revision = 'f98c730d6527'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('message1', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('message2', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('progress1', sa.Double(), nullable=True))
        batch_op.drop_column('progress_string')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('progress_string', mysql.VARCHAR(length=50), nullable=True))
        batch_op.drop_column('progress1')
        batch_op.drop_column('message2')
        batch_op.drop_column('message1')

    # ### end Alembic commands ###