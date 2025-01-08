"""Create usage logs table.

Revision ID: f0b5f4d7cbb8
Revises: 6e722b0ef2e8
Create Date: 2023-11-16 23:02:38.131343
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f0b5f4d7cbb8'
down_revision: Union[str, None] = '3b4792c14466'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'usage_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_key', sa.String, nullable=False),
        sa.Column('source_id', sa.Integer, nullable=False),
        sa.Column('operation', sa.String, nullable=False),
        sa.Column('input_usage', sa.Integer, nullable=False, default=0),
        sa.Column('output_usage', sa.Integer, nullable=False, default=0),
        sa.Column('embedding_usage', sa.Integer, nullable=False, default=0),
        sa.Column('price', sa.Float, nullable=False, default=0),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
    )


def downgrade() -> None:
    op.drop_table('usage_logs')
