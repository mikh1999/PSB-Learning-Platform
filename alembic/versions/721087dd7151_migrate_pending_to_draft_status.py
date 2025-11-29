"""migrate pending to draft status

Revision ID: 721087dd7151
Revises: 8098f5cc71b7
Create Date: 2025-11-28 22:33:04.827711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '721087dd7151'
down_revision: Union[str, None] = '8098f5cc71b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Обновляем существующие записи: PENDING -> DRAFT
    op.execute("UPDATE submissions SET status = 'DRAFT' WHERE status = 'PENDING'")


def downgrade() -> None:
    # Возвращаем DRAFT -> PENDING
    op.execute("UPDATE submissions SET status = 'PENDING' WHERE status = 'DRAFT'")
