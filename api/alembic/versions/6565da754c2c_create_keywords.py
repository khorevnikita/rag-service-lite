"""Create keywords.

Revision ID: 6565da754c2c
Revises: dc40a5a49693
Create Date: 2023-12-28 20:25:05.150690
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6565da754c2c'
down_revision: Union[str, None] = 'f5d879539355'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'keywords',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, nullable=False, index=True),
        sa.Column('text', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
    )

    op.create_table(
        'document_keyword',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('document_id', sa.Integer, nullable=False, index=True),
        sa.Column('keyword_id', sa.Integer, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('document_keyword')
    op.drop_table('keywords')
