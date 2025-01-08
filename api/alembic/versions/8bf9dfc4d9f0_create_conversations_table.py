"""Create conversations table.

Revision ID: 8bf9dfc4d9f0
Revises: f9a4b54299dc
Create Date: 2024-01-11 22:19:23.827958
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import Column, Integer
from sqlalchemy.types import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8bf9dfc4d9f0'
down_revision: Union[str, None] = 'f9a4b54299dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('meta', JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.text("NOW()")),
        sa.Column('updated_at', sa.DateTime, default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
        sa.ForeignKeyConstraint(
            ['account_id'],
            ['accounts.id'],
        ),
    )

    op.add_column('questions', Column('conversation_id', Integer, nullable=True))
    op.create_foreign_key(
        'questions_conversation_id_fkey',
        'questions',
        'conversations',
        ['conversation_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'questions_conversation_id_fkey', 'questions', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('questions', 'conversation_id')

    op.drop_table('conversations')
