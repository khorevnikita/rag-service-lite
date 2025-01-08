"""Create settings table.

Revision ID: f5d879539355
Revises: 5b71267053e5
Create Date: 2023-12-20 16:41:55.452547
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f5d879539355'
down_revision: Union[str, None] = '5b71267053e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('account_id', sa.Integer, nullable=False, index=True),
        sa.Column('key', sa.String, nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('settings')
