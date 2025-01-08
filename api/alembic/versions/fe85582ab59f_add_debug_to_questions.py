"""Add debug to questions.

Revision ID: fe85582ab59f
Revises: 8394e1615dfd
Create Date: 2024-01-27 20:33:41.197279
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fe85582ab59f'
down_revision: Union[str, None] = '8394e1615dfd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('questions', sa.Column('keyword', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'keyword')
