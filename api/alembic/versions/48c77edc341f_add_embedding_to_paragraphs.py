"""Add embedding to paragraphs.

Revision ID: 48c77edc341f
Revises: 9e4f2aa573a7
Create Date: 2024-01-04 18:38:24.079805
"""

# pylint: disable=no-member

from typing import Sequence, Union

from sqlalchemy import Column, DateTime, String

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '48c77edc341f'
down_revision: Union[str, None] = '9e4f2aa573a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('paragraphs', Column('embedding_url', String, nullable=True))
    op.add_column('paragraphs', Column('embedded_at', DateTime, nullable=True))


def downgrade() -> None:
    op.drop_column('paragraphs', 'embedded_at')
    op.drop_column('paragraphs', 'embedding_url')
