"""<%text>${message}</%text>

Revision ID: <%text>${up_revision}</%text>
Revises: <%text>${down_revision | comma,n}</%text>
Create Date: <%text>${create_date}</%text>

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
<%text>${imports if imports else ""}</%text>

# revision identifiers, used by Alembic.
revision: str = <%text>${repr(up_revision)}</%text>
down_revision: Union[str, None] = <%text>${repr(down_revision)}</%text>
branch_labels: Union[str, Sequence[str], None] = <%text>${repr(branch_labels)}</%text>
depends_on: Union[str, Sequence[str], None] = <%text>${repr(depends_on)}</%text>


def upgrade() -> None:
    <%text>${upgrades if upgrades else "pass"}</%text>


def downgrade() -> None:
    <%text>${downgrades if downgrades else "pass"}</%text>
