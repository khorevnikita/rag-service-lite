"""Save hit score in question.

Revision ID: 8394e1615dfd
Revises: 08e4159c1f89
Create Date: 2024-01-27 13:01:18.541793
"""

# pylint: disable=no-member

from typing import Sequence, Union

from sqlalchemy import Column, Float

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8394e1615dfd'
down_revision: Union[str, None] = '08e4159c1f89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('paragraph_question', Column('score', Float, nullable=True))


def downgrade() -> None:
    op.drop_column('paragraph_question', 'score')
