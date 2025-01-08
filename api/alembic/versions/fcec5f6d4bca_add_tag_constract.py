"""Add tag constract.

Revision ID: fcec5f6d4bca
Revises: 53f115bd54d0
Create Date: 2024-04-29 20:19:30.806415
"""

# pylint: disable=no-member

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'fcec5f6d4bca'
down_revision: Union[str, None] = '53f115bd54d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('unique_account_text', 'keywords', ['text', 'account_id'])


def downgrade() -> None:
    op.drop_constraint('unique_account_text', 'keywords', type_='unique')
