"""make orders

Revision ID: c8131acbfffb
Revises: 30666042f2a4
Create Date: 2024-01-29 23:05:02.728871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8131acbfffb'
down_revision = '30666042f2a4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('lastChangeDate', sa.TIMESTAMP(), nullable=True),
    sa.Column('warehouseName', sa.String(), nullable=True),
    sa.Column('countryName', sa.String(), nullable=True),
    sa.Column('oblastOkrugName', sa.String(), nullable=True),
    sa.Column('regionName', sa.String(), nullable=True),
    sa.Column('supplierArticle', sa.String(), nullable=False),
    sa.Column('nmId', sa.Integer(), nullable=True),
    sa.Column('barcode', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=False),
    sa.Column('subject', sa.String(), nullable=False),
    sa.Column('brand', sa.String(), nullable=False),
    sa.Column('techSize', sa.String(), nullable=False),
    sa.Column('incomeID', sa.Integer(), nullable=True),
    sa.Column('isSupply', sa.Boolean(), nullable=True),
    sa.Column('isRealization', sa.Boolean(), nullable=True),
    sa.Column('totalPrice', sa.Float(), nullable=True),
    sa.Column('discountPercent', sa.Float(), nullable=True),
    sa.Column('spp', sa.Integer(), nullable=True),
    sa.Column('finishedPrice', sa.Float(), nullable=True),
    sa.Column('priceWithDisc', sa.Float(), nullable=True),
    sa.Column('isCancel', sa.Boolean(), nullable=True),
    sa.Column('cancelDate', sa.TIMESTAMP(), nullable=True),
    sa.Column('orderType', sa.String(), nullable=True),
    sa.Column('sticker', sa.String(), nullable=True),
    sa.Column('gNumber', sa.String(), nullable=True),
    sa.Column('srid', sa.String(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    # ### end Alembic commands ###
