"""Create users and todos tables

Revision ID: 001
Revises:
Create Date: 2026-01-02 01:15:00.000000

This migration creates the initial database schema for the Phase II todo application:
- users table with authentication fields
- todos table with user isolation via foreign key
- All required indexes for query performance
- Foreign key constraint with CASCADE delete

Spec Reference: specs/001-fullstack-web-app/data-model.md
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create users and todos tables with all constraints and indexes."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=60), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_users'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )

    # Create index on email (unique index for login queries)
    op.create_index('idx_users_email', 'users', ['email'], unique=True)

    # Create todos table
    op.create_table(
        'todos',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('priority', sa.String(length=10), server_default='medium', nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint("priority IN ('low', 'medium', 'high')", name='check_todos_priority'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_todos_user_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_todos')
    )

    # Create indexes for todos table (performance optimization)
    # Foreign key index (critical for user isolation queries)
    op.create_index('idx_todos_user_id', 'todos', ['user_id'], unique=False)

    # Filter indexes (for status, priority, date filtering)
    op.create_index('idx_todos_completed', 'todos', ['completed'], unique=False)
    op.create_index('idx_todos_priority', 'todos', ['priority'], unique=False)
    op.create_index('idx_todos_created_at', 'todos', ['created_at'], unique=False)

    # Search index (for title search queries)
    op.create_index('idx_todos_title', 'todos', ['title'], unique=False)

    # Composite indexes for common query patterns
    op.create_index('idx_todos_user_completed', 'todos', ['user_id', 'completed'], unique=False)
    op.create_index('idx_todos_user_priority', 'todos', ['user_id', 'priority'], unique=False)


def downgrade():
    """Drop all tables and indexes (rollback migration)."""

    # Drop todos table (will cascade drop all indexes)
    op.drop_table('todos')

    # Drop users table (will cascade drop all indexes)
    op.drop_table('users')
