"""Fix conversation and message id columns to use SERIAL autoincrement

Revision ID: 002
Revises: 001
Create Date: 2026-02-12 00:00:00.000000

The Phase 3 conversation and message tables were created by SQLModel create_all()
with UUID id columns and no auto-increment default. The models expect integer
auto-increment ids. This migration drops and recreates them with proper SERIAL PKs.

Phase 3 tables use singular names (user, conversation, message, task).
The user.id is UUID, so conversation.user_id must be UUID/VARCHAR to match.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Recreate Phase 3 conversation and message tables with proper SERIAL id columns."""

    # Drop message first (has FK to conversation)
    op.execute("DROP TABLE IF EXISTS message CASCADE")
    # Drop conversation
    op.execute("DROP TABLE IF EXISTS conversation CASCADE")

    # Recreate conversation table with SERIAL id
    # user_id references Phase 3 "user" table which has UUID id
    op.execute("""
        CREATE TABLE conversation (
            id SERIAL PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            title VARCHAR(255),
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now(),
            is_active BOOLEAN NOT NULL DEFAULT true
        )
    """)
    op.execute("CREATE INDEX idx_conversation_user_id ON conversation(user_id)")

    # Recreate message table with SERIAL id
    op.execute("""
        CREATE TABLE message (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL DEFAULT 'user',
            content TEXT NOT NULL,
            "timestamp" TIMESTAMP NOT NULL DEFAULT now(),
            message_metadata TEXT
        )
    """)
    op.execute("CREATE INDEX idx_message_conversation_id ON message(conversation_id)")


def downgrade():
    """Drop recreated tables."""
    op.execute("DROP TABLE IF EXISTS message CASCADE")
    op.execute("DROP TABLE IF EXISTS conversation CASCADE")
