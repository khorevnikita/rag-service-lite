"""Add tags to paragraphs.

Revision ID: 08e4159c1f89
Revises: 8bf9dfc4d9f0
Create Date: 2024-01-16 20:37:23.688668
"""

# pylint: disable=no-member

from typing import Sequence, Union

from sqlalchemy import Column
from sqlalchemy.types import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '08e4159c1f89'
down_revision: Union[str, None] = '8bf9dfc4d9f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('paragraphs', Column('keywords', JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('paragraphs', 'keywords')
