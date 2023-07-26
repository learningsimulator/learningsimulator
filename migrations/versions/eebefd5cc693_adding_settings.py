"""Adding Settings

Revision ID: eebefd5cc693
Revises: 
Create Date: 2022-09-22 21:42:37.054342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eebefd5cc693'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('graph_lib', sa.String(length=6), nullable=True),
    sa.Column('plot_orientation', sa.Enum('horizontal', 'vertical', name='orientation'), nullable=True),
    sa.Column('plo_width', sa.Integer(), nullable=True),
    sa.Column('plot_height', sa.Integer(), nullable=True),
    sa.Column('legend_x', sa.Float(), nullable=True),
    sa.Column('legend_y', sa.Float(), nullable=True),
    sa.Column('legend_x_anchor', sa.String(length=6), nullable=True),
    sa.Column('legend_y_anchor', sa.String(length=6), nullable=True),
    sa.Column('legend_orientation', sa.Enum('horizontal', 'vertical', name='orientation'), nullable=True),
    sa.Column('paper_color', sa.String(length=7), nullable=True),
    sa.Column('plot_bgcolor', sa.String(length=7), nullable=True),
    sa.Column('mplpdf', sa.Boolean(), nullable=True),
    sa.Column('keep_plots', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('settings_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'settings', ['settings_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('settings_id')

    op.drop_table('settings')
    # ### end Alembic commands ###