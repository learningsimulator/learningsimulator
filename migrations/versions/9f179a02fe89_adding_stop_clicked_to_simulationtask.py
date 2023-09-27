"""Adding stop_clicked to SimulationTask

Revision ID: 9f179a02fe89
Revises: c60c38f00ac8
Create Date: 2023-05-01 23:12:47.775936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f179a02fe89'
down_revision = 'c60c38f00ac8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('stop_clicked', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('simulation_task', schema=None) as batch_op:
        batch_op.drop_column('stop_clicked')

    # ### end Alembic commands ###