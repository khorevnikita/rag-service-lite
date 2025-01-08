"""Create questions table.

Revision ID: 8b17582c5ced
Revises: f21e941f52ec
Create Date: 2023-11-30 00:55:30.412745
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8b17582c5ced'
down_revision: Union[str, None] = 'f21e941f52ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('answer', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.Column('answered_at', sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    pass
