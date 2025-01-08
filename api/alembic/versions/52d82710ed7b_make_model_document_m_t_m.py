"""Make model_document m-t-m.

Revision ID: 52d82710ed7b
Revises: 4d538a864386
Create Date: 2023-12-29 17:08:51.444776
"""

# pylint: disable=no-member

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '52d82710ed7b'
down_revision: Union[str, None] = '6565da754c2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

models_document_id_fk_name = 'models_document_id_fkey'
document_model_table_name = 'document_model'


def upgrade() -> None:
    # Создать пивот-таблицу
    op.create_table(
        document_model_table_name,
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('document_id', sa.Integer, nullable=False, index=True),
        sa.Column('model_id', sa.Integer, nullable=False, index=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now, onupdate=sa.func.now),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['model_id'], ['models.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    # Удалить пивот-таблицу
    op.drop_table(document_model_table_name)
