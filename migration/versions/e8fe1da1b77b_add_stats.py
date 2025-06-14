"""add stats

Revision ID: e8fe1da1b77b
Revises: 92ea312d9895
Create Date: 2024-01-31 01:25:52.687271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8fe1da1b77b'
down_revision = '92ea312d9895'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('nmId', sa.Integer(), nullable=True),
    sa.Column('vendorCode', sa.String(), nullable=True),
    sa.Column('brandName', sa.String(), nullable=True),
    sa.Column('openCardCount', sa.Integer(), nullable=True),
    sa.Column('addToCartCount', sa.Integer(), nullable=True),
    sa.Column('ordersCount', sa.Integer(), nullable=True),
    sa.Column('ordersSumRub', sa.Float(), nullable=True),
    sa.Column('buyoutsCount', sa.Integer(), nullable=True),
    sa.Column('buyoutsSumRub', sa.Float(), nullable=True),
    sa.Column('cancelCount', sa.Integer(), nullable=True),
    sa.Column('cancelSumRub', sa.Float(), nullable=True),
    sa.Column('addToCartPercent', sa.Float(), nullable=True),
    sa.Column('cartToOrderPercent', sa.Float(), nullable=True),
    sa.Column('buyoutsPercent', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stats_id'), 'stats', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_stats_id'), table_name='stats')
    op.drop_table('stats')
    # ### end Alembic commands ###
