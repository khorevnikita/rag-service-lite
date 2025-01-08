"""Create paragraph table.

Revision ID: 3b4792c14466
Revises: 6e468a965aab
Create Date: 2023-11-10 20:07:38.603567
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '3b4792c14466'
down_revision: Union[str, None] = '774837ebcfda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'paragraphs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('document_id', sa.Integer, nullable=False, index=True),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('content_url', sa.String, nullable=False),
        sa.Column('content_length', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('paragraphs')
