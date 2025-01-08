"""add_tools_to_questions.

Revision ID: 053f8780fa07
Revises: 1b4ec4081481
Create Date: 2024-12-18 17:31:46.171762
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '053f8780fa07'
down_revision: Union[str, None] = '1b4ec4081481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('questions', sa.Column('available_tools', sa.JSON(), nullable=True))
    op.add_column('questions', sa.Column('called_tools', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'available_tools')
    op.drop_column('questions', 'called_tools')
