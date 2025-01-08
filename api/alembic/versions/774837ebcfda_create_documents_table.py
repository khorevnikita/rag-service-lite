"""Create documents table.

Revision ID: 774837ebcfda
Revises: 3b4792c14466
Create Date: 2023-11-10 20:33:33.098728
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '774837ebcfda'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('name', sa.String, nullable=True),
        sa.Column(
            'url',
            sa.Text,
            nullable=False,
        ),
        sa.Column('content_length', sa.Integer, nullable=True),
        sa.Column('content_url', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
    )


def downgrade() -> None:
    op.drop_table('documents')
