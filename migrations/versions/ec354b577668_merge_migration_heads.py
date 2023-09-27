"""merge migration heads

Revision ID: ec354b577668
Revises: 043330a4ac72, 70d012ea0252
Create Date: 2023-09-23 18:14:20.371531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec354b577668'
down_revision = ('043330a4ac72', '70d012ea0252')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
