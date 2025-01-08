"""Add model pricing.

Revision ID: f9a4b54299dc
Revises: 48c77edc341f
Create Date: 2024-01-04 20:35:13.779147
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f9a4b54299dc'
down_revision: Union[str, None] = '48c77edc341f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('models', sa.Column('input', sa.Float(), nullable=True))
    op.add_column('models', sa.Column('output', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('models', 'input')
    op.drop_column('models', 'output')
