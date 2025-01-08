"""Create account table.

Revision ID: 5b71267053e5
Revises: c5770748f6b4
Create Date: 2023-12-20 15:45:19.144862
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import Column, Integer

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5b71267053e5'
down_revision: Union[str, None] = 'c5770748f6b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('login', sa.String, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
    )

    op.add_column('documents', Column('account_id', Integer, nullable=True))
    op.create_foreign_key(
        'documents_account_id_fkey',
        'documents',
        'accounts',
        ['account_id'],
        ['id'],
        ondelete='SET NULL',
    )

    op.add_column('questions', Column('account_id', Integer, nullable=True))
    op.create_foreign_key(
        'questions_account_id_fkey',
        'questions',
        'accounts',
        ['account_id'],
        ['id'],
        ondelete='SET NULL',
    )

    op.add_column('models', Column('account_id', Integer, nullable=True))
    op.create_foreign_key(
        'models_account_id_fkey',
        'models',
        'accounts',
        ['account_id'],
        ['id'],
        ondelete='SET NULL',
    )

    op.add_column('usage_logs', Column('account_id', Integer, nullable=True))
    op.create_foreign_key(
        'usage_logs_account_id_fkey',
        'usage_logs',
        'accounts',
        ['account_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint(
        'documents_account_id_fkey', 'documents', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('documents', 'account_id')

    op.drop_constraint(
        'questions_account_id_fkey', 'questions', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('questions', 'account_id')

    op.drop_constraint(
        'models_account_id_fkey', 'models', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('models', 'account_id')

    op.drop_constraint(
        'usage_logs_account_id_fkey', 'usage_logs', type_='foreignkey'
    )  # Имя ограничения может отличаться
    op.drop_column('usage_logs', 'account_id')

    op.drop_table('accounts')
