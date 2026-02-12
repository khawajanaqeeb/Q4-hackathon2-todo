"""Fix Phase 3 tables to use SERIAL autoincrement for id columns

Revision ID: 003
Revises: 002
Create Date: 2026-02-13 00:00:00.000000

Tables created by SQLModel.metadata.create_all() got UUID id columns with no
default. The models expect integer auto-increment ids. This migration drops and
recreates audit_logs, mcp_tools, and api_keys with proper SERIAL PKs.

The user.id is UUID in the actual database, so user_id FKs use UUID type.
The task table already has SERIAL auto-increment (id_seq) so is skipped.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Recreate Phase 3 tables with proper SERIAL id columns."""

    # --- audit_logs ---
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
    op.execute("""
        CREATE TABLE audit_logs (
            id SERIAL PRIMARY KEY,
            user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
            action_type VARCHAR NOT NULL,
            resource_type VARCHAR,
            resource_id INTEGER,
            log_metadata JSON,
            success BOOLEAN NOT NULL DEFAULT true,
            response_time_ms INTEGER,
            ip_address VARCHAR,
            user_agent VARCHAR,
            error_message VARCHAR,
            timestamp TIMESTAMP NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id)")
    op.execute("CREATE INDEX idx_audit_logs_action_type ON audit_logs(action_type)")
    op.execute("CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp)")

    # --- mcp_tools ---
    op.execute("DROP TABLE IF EXISTS mcp_tools CASCADE")
    op.execute("""
        CREATE TABLE mcp_tools (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL UNIQUE,
            description VARCHAR,
            provider VARCHAR NOT NULL,
            tool_schema JSON NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now(),
            user_id UUID
        )
    """)

    # --- api_keys ---
    op.execute("DROP TABLE IF EXISTS api_keys CASCADE")
    op.execute("""
        CREATE TABLE api_keys (
            id SERIAL PRIMARY KEY,
            provider VARCHAR NOT NULL,
            user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
            encrypted_key BYTEA NOT NULL,
            encrypted_key_iv BYTEA NOT NULL,
            encrypted_key_salt BYTEA NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            expires_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT now(),
            updated_at TIMESTAMP NOT NULL DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_api_keys_user_id ON api_keys(user_id)")


def downgrade():
    """Drop recreated tables."""
    op.execute("DROP TABLE IF EXISTS api_keys CASCADE")
    op.execute("DROP TABLE IF EXISTS mcp_tools CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
