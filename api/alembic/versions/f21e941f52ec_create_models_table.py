"""Create models table.

Revision ID: f21e941f52ec
Revises: f0b5f4d7cbb8
Create Date: 2023-11-26 14:52:43.239216
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f21e941f52ec'
down_revision: Union[str, None] = 'f0b5f4d7cbb8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'models',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('base_model_name', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
    )


def downgrade() -> None:
    op.drop_table('models')
