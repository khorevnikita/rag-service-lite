"""add_response_format_to_questions

Revision ID: 23fbdb0f5674
Revises: 8cd7789de89b
Create Date: 2025-01-15 01:00:56.856580

"""
from typing import Sequence, Union
from sqlalchemy.dialects.postgresql import ENUM

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23fbdb0f5674'
down_revision: Union[str, None] = '8cd7789de89b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create a new ENUM type
    answer_format_enum = ENUM('text', 'audio', name='answerformat')
    answer_format_enum.create(op.get_bind(), checkfirst=True)

    # Add the new column
    op.add_column('questions', sa.Column('answer_format', answer_format_enum, nullable=True))
    op.add_column('questions', sa.Column('audio_file', sa.String(), nullable=True))


def downgrade():
    # Remove the column
    op.drop_column('questions', 'audio_file')
    op.drop_column('questions', 'answer_format')

    # Drop the ENUM type
    answer_format_enum = ENUM('text', 'audio', name='answerformat')
    answer_format_enum.drop(op.get_bind(), checkfirst=True)
