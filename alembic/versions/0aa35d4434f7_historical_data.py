"""historical_data

Revision ID: 0aa35d4434f7
Revises: 20d94574df07
Create Date: 2024-02-29 22:18:18.002547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0aa35d4434f7'
down_revision: Union[str, None] = '20d94574df07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'historical_data',
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
        sa.Column('date', sa.Date, nullable=False),
    )

    op.create_index('idx_historical_data_name', 'historical_data', ['name'])
    op.create_index('idx_historical_data_date', 'historical_data', ['date'])

def downgrade() -> None:
    op.drop_index('idx_historical_data_date', table_name='historical_data')
    op.drop_index('idx_historical_data_name', table_name='historical_data')
    op.drop_table('historical_data')