"""Add reactions to questions.

Revision ID: c5770748f6b4
Revises: 8b17582c5ced
Create Date: 2023-12-07 21:56:32.728576
"""

# pylint: disable=no-member

from typing import Sequence, Union

from sqlalchemy import Column, DateTime, Integer, String

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c5770748f6b4'
down_revision: Union[str, None] = '8b17582c5ced'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('questions', Column('reaction', String, nullable=True))
    op.add_column('questions', Column('reacted_at', DateTime, nullable=True))
    op.add_column('questions', Column('model_id', Integer, nullable=True))
    op.create_foreign_key(
        'questions_model_id_fkey',
        'questions',
        'models',
        ['model_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'questions_model_id_fkey', 'questions', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('questions', 'model_id')
    op.drop_column('questions', 'reacted_at')
    op.drop_column('questions', 'reaction')
