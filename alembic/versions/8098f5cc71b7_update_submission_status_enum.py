"""update submission status enum

Revision ID: 8098f5cc71b7
Revises: 57721c166387
Create Date: 2025-11-28 22:21:21.912818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8098f5cc71b7'
down_revision: Union[str, None] = '57721c166387'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем новые значения в enum (в отдельных транзакциях)
    op.execute("COMMIT")
    op.execute("ALTER TYPE submissionstatus ADD VALUE IF NOT EXISTS 'DRAFT'")
    op.execute("ALTER TYPE submissionstatus ADD VALUE IF NOT EXISTS 'RETURNED'")


def downgrade() -> None:
    pass  # Удаление значений enum в PostgreSQL сложно, оставляем как есть
