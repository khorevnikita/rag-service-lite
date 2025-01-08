"""add_supertokens_id

Revision ID: 8cd7789de89b
Revises: 053f8780fa07
Create Date: 2024-12-31 16:21:25.001567

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8cd7789de89b'
down_revision: Union[str, None] = '053f8780fa07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('accounts', sa.Column('supertokens_id', sa.UUID))
    op.add_column('accounts', sa.Column('is_active', sa.Boolean, default=False))


def downgrade() -> None:
    op.drop_column('accounts', 'supertokens_id')
    op.drop_column('accounts', 'is_active')
