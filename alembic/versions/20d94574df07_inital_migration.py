"""Inital migration

Revision ID: 20d94574df07
Revises: 
Create Date: 2024-02-19 17:12:56.034260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20d94574df07'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cryptocurrencies',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('rank', sa.Integer),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price', sa.Numeric),
        sa.Column('percent_change_1h', sa.Numeric),
        sa.Column('percent_change_24h', sa.Numeric),
        sa.Column('percent_change_7d', sa.Numeric),
        sa.Column('market_cap', sa.Numeric),
        sa.Column('volume_24h', sa.Numeric),
        sa.Column('circulating_supply', sa.Numeric),
        sa.Column('last_update', sa.TIMESTAMP, nullable=False),
        sa.UniqueConstraint('name', 'last_update', name='unique_name_last_update')
    )

    op.create_index('idx_cryptocurrencies_name', 'cryptocurrencies', ['name'])
    op.create_index('idx_cryptocurrencies_last_update', 'cryptocurrencies', ['last_update'])

def downgrade() -> None:
    op.drop_index('idx_cryptocurrencies_last_update', table_name='cryptocurrencies')
    op.drop_index('idx_cryptocurrencies_name', table_name='cryptocurrencies')
    op.drop_table('cryptocurrencies')