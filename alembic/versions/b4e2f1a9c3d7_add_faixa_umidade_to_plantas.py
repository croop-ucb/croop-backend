"""add_faixa_umidade_to_plantas

Revision ID: b4e2f1a9c3d7
Revises: 93cc187eda7c
Create Date: 2026-06-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4e2f1a9c3d7"
down_revision: Union[str, None] = "93cc187eda7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("plantas", sa.Column("faixa_umidade_min", sa.Numeric(5, 2), nullable=True))
    op.add_column("plantas", sa.Column("faixa_umidade_max", sa.Numeric(5, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("plantas", "faixa_umidade_max")
    op.drop_column("plantas", "faixa_umidade_min")
