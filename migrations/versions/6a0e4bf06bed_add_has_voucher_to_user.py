"""add_has_voucher_to_user

Revision ID: 6a0e4bf06bed
Revises: a82b6c7d9e1f
Create Date: 2025-12-26 18:13:31.679799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0e4bf06bed'
down_revision: Union[str, None] = 'a82b6c7d9e1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('has_voucher', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('users', 'has_voucher')
