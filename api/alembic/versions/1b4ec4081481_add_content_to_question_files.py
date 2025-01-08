"""add_content_to_question_files.

Revision ID: 1b4ec4081481
Revises: a534e4d9fc7a
Create Date: 2024-11-19 15:43:45.756615
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1b4ec4081481'
down_revision: Union[str, None] = 'fcec5f6d4bca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('question_files', sa.Column('content', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('question_files', 'content')
