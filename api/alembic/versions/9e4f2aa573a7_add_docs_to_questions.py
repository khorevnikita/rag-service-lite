"""Add docs to questions.

Revision ID: 9e4f2aa573a7
Revises: f414485eb1c5
Create Date: 2024-01-03 16:52:42.342224
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import Column, String

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9e4f2aa573a7'
down_revision: Union[str, None] = '52d82710ed7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'paragraph_question',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('paragraph_id', sa.Integer, nullable=False, index=True),
        sa.Column('question_id', sa.Integer, nullable=False, index=True),
        sa.Column('document_id', sa.Integer, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['paragraph_id'], ['paragraphs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    )

    op.add_column('questions', Column('mode', String, nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'mode')
    op.drop_table('paragraph_question')
