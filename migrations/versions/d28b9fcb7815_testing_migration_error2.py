"""Testing migration error2.

Revision ID: d28b9fcb7815
Revises: 91b55719bfb7
Create Date: 2022-10-20 10:15:59.517606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd28b9fcb7815'
down_revision = '91b55719bfb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('foo', sa.String(length=3), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'foo')
    # ### end Alembic commands ###
