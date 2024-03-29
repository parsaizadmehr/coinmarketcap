"""create users table for telegram bot

Revision ID: b9efb8ee7328
Revises: 0aa35d4434f7
Create Date: 2024-03-23 15:35:26.587910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b9efb8ee7328'
down_revision: Union[str, None] = '0aa35d4434f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('uid', sa.Integer, nullable=True)  # Assuming uid can be nullable
    )


def downgrade() -> None:
    op.drop_table('users')
