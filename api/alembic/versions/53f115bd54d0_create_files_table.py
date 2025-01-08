"""Create files table.

Revision ID: 53f115bd54d0
Revises: b8a52696bac8
Create Date: 2024-03-29 21:18:51.449255
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '53f115bd54d0'
down_revision: Union[str, None] = '057bb14b5e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'question_files',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('conversation_id', sa.Integer, nullable=False, index=True),
        sa.Column('question_id', sa.Integer, nullable=False, index=True),
        sa.Column('url', sa.String, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('extension', sa.String, nullable=False),
        sa.Column('size', sa.Integer, nullable=False),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('is_private', sa.Boolean, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('question_files')
