"""Altering fields.

Revision ID: d5149d86879a
Revises: fc52d6fa7468
Create Date: 2023-02-25 23:16:17.684740

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'd5149d86879a'
down_revision = 'fc52d6fa7468'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('id_predef', table_name='script')
    op.drop_table('script')
    op.add_column('settings', sa.Column('file_type_mpl', sa.String(length=3), nullable=True))
    op.add_column('settings', sa.Column('file_type_plotly', sa.String(length=4), nullable=True))
    op.drop_column('settings', 'file_type')
    op.drop_column('settings', 'legend_x')
    op.drop_column('settings', 'legend_y')
    op.drop_column('settings', 'legend_y_anchor')
    op.drop_column('settings', 'legend_x_anchor')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('legend_x_anchor', mysql.VARCHAR(length=6), nullable=True))
    op.add_column('settings', sa.Column('legend_y_anchor', mysql.VARCHAR(length=6), nullable=True))
    op.add_column('settings', sa.Column('legend_y', mysql.FLOAT(), nullable=True))
    op.add_column('settings', sa.Column('legend_x', mysql.FLOAT(), nullable=True))
    op.add_column('settings', sa.Column('file_type', mysql.VARCHAR(length=3), nullable=True))
    op.drop_column('settings', 'file_type_plotly')
    op.drop_column('settings', 'file_type_mpl')
    op.create_table('script',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('id_predef', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('code', mysql.VARCHAR(length=10000), nullable=True),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='script_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('id_predef', 'script', ['id_predef'], unique=False)
    # ### end Alembic commands ###
