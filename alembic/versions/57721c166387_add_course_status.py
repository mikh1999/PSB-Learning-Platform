"""add course status

Revision ID: 57721c166387
Revises: 6eea7b137e13
Create Date: 2025-11-28 22:12:03.509173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57721c166387'
down_revision: Union[str, None] = '6eea7b137e13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    coursestatus = sa.Enum('DRAFT', 'PUBLISHED', name='coursestatus')
    coursestatus.create(op.get_bind(), checkfirst=True)
    op.add_column('courses', sa.Column('status', coursestatus, nullable=False, server_default='DRAFT'))


def downgrade() -> None:
    op.drop_column('courses', 'status')
    sa.Enum(name='coursestatus').drop(op.get_bind(), checkfirst=True)
