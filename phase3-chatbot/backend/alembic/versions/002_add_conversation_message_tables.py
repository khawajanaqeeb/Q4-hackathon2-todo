"""Add Conversation and Message models for Phase 3 AI Chatbot.

Revision ID: 002_add_conversation_message_tables
Revises: 001_create_users_and_todos_tables
Create Date: 2024-01-20 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import uuid
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002_add_conversation_message_tables'
down_revision: Union[str, None] = '001_create_users_and_todos_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, server_default='New Conversation'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_conversations_user_id', 'user_id'),  # Index on user_id
        sa.Index('ix_conversations_created_at', 'created_at'),  # Index on created_at
        sa.Index('ix_conversations_is_active', 'is_active')  # Index on is_active
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', 'TOOL', name='messagerole', native_enum=False), nullable=False),
        sa.Column('content', sa.Text(), nullable=False, server_default=''),
        sa.Column('status', sa.Enum('PENDING', 'PROCESSED', 'ERROR', name='messagestatus', native_enum=False), nullable=False, server_default='PROCESSED'),
        sa.Column('tool_name', sa.String(length=100), nullable=True),
        sa.Column('tool_input', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('tool_output', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_messages_conversation_id', 'conversation_id'),  # Index on conversation_id
        sa.Index('ix_messages_role', 'role'),  # Index on role
        sa.Index('ix_messages_created_at', 'created_at'),  # Index on created_at
        sa.Index('ix_messages_status', 'status')  # Index on status
    )


def downgrade() -> None:
    # Drop messages table
    op.drop_table('messages')

    # Drop conversations table
    op.drop_table('conversations')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS messagerole;")
    op.execute("DROP TYPE IF EXISTS messagestatus;")