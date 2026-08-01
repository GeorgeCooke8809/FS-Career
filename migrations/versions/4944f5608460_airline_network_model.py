"""airline network model

Revision ID: 4944f5608460
Revises: 897a9ded0b7e
Create Date: 2026-08-01 13:51:34.219437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4944f5608460'
down_revision: Union[str, Sequence[str], None] = '897a9ded0b7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("airlines") as batch_op:
        batch_op.add_column(sa.Column("network_model", sa.String(length=16), nullable=True))
        batch_op.create_check_constraint(
            "ck_airline_network_model_valid",
            "network_model IN ('hub_and_spoke', 'point_to_point')",
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("airlines") as batch_op:
        batch_op.drop_constraint("ck_airline_network_model_valid", type_="check")
        batch_op.drop_column("network_model")
