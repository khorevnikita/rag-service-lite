"""Add sources to documents.

Revision ID: 057bb14b5e4b
Revises: 744f1cc85b4e
Create Date: 2024-03-15 19:04:39.504693
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '057bb14b5e4b'
down_revision: Union[str, None] = 'fe85582ab59f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('meta', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'meta')
