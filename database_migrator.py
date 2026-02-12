#!/usr/bin/env python3
"""
Database Migration Script: Legacy to Canonical Tables

This script migrates data from legacy tables to canonical tables:
- users → user (with UUID conversion)
- todos → task (with UUID conversion)
"""

import uuid
from sqlmodel import create_engine, Session, select
from typing import Dict
import json
import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), "phase3-chatbot", "backend")
sys.path.insert(0, backend_path)

def migrate_database():
    """Main migration function"""
    print("Starting database migration...")

    # Import models inside the function to avoid import issues
    from src.models.user import User as CanonicalUser
    from src.models.task import Task as CanonicalTask, PriorityLevel
    from app.models.user import User as LegacyUser
    from app.models.todo import Todo as LegacyTodo
    from src.database import DATABASE_URL

    # Create engine and session
    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Create backup mappings
        user_id_mapping: Dict[int, uuid.UUID] = {}

        print("Step 1: Migrating users...")
        # Get all legacy users
        legacy_users = session.exec(select(LegacyUser)).all()

        for legacy_user in legacy_users:
            # Create new canonical user
            canonical_user = CanonicalUser(
                id=uuid.uuid4(),  # Generate new UUID
                username=legacy_user.name or f"user_{legacy_user.id}",
                email=legacy_user.email,
                hashed_password=legacy_user.hashed_password,
                is_active=legacy_user.is_active,
                is_superuser=False,  # Default value
                created_at=legacy_user.created_at,
                updated_at=legacy_user.updated_at
            )

            session.add(canonical_user)
            session.flush()  # Get the new ID

            # Map legacy ID to new UUID
            user_id_mapping[legacy_user.id] = canonical_user.id
            print(f"  Migrated user {legacy_user.id} -> {canonical_user.id}")

        session.commit()
        print(f"  Migrated {len(legacy_users)} users")

        print("Step 2: Migrating todos to tasks...")
        # Get all legacy todos
        legacy_todos = session.exec(select(LegacyTodo)).all()

        migrated_tasks = 0
        for legacy_todo in legacy_todos:
            # Get the corresponding canonical user ID
            if legacy_todo.user_id not in user_id_mapping:
                print(f"  Warning: Todo {legacy_todo.id} has invalid user_id {legacy_todo.user_id}, skipping...")
                continue

            canonical_user_id = user_id_mapping[legacy_todo.user_id]

            # Convert priority from legacy format to canonical format
            priority_map = {
                'low': PriorityLevel.LOW,
                'medium': PriorityLevel.MEDIUM,
                'high': PriorityLevel.HIGH
            }
            canonical_priority = priority_map.get(legacy_todo.priority.value, PriorityLevel.MEDIUM)

            # Convert tags from JSON array to string
            tags_str = json.dumps(legacy_todo.tags) if legacy_todo.tags else None

            # Create new canonical task
            canonical_task = CanonicalTask(
                id=uuid.uuid4(),  # Generate new UUID
                user_id=canonical_user_id,
                title=legacy_todo.title,
                description=legacy_todo.description,
                priority=canonical_priority,
                due_date=None,  # Legacy todos don't have due dates
                completed=legacy_todo.completed,
                tags=tags_str,
                created_at=legacy_todo.created_at,
                updated_at=legacy_todo.updated_at
            )

            session.add(canonical_task)
            migrated_tasks += 1
            print(f"  Migrated todo {legacy_todo.id} -> {canonical_task.id}")

        session.commit()
        print(f"  Migrated {migrated_tasks} todos to tasks")

        print("Step 3: Migration completed successfully!")

        # Print summary
        canonical_users_count = session.exec(select(CanonicalUser)).count()
        canonical_tasks_count = session.exec(select(CanonicalTask)).count()

        print(f"\nMigration Summary:")
        print(f"  Legacy users: {len(legacy_users)} -> Canonical users: {canonical_users_count}")
        print(f"  Legacy todos: {len(legacy_todos)} -> Canonical tasks: {canonical_tasks_count}")
        print(f"  User ID mappings created: {len(user_id_mapping)}")


def verify_migration():
    """Verify the migration was successful"""
    print("\nVerifying migration...")

    # Import models inside the function to avoid import issues
    from src.models.user import User as CanonicalUser
    from src.models.task import Task as CanonicalTask
    from app.models.user import User as LegacyUser
    from app.models.todo import Todo as LegacyTodo
    from src.database import DATABASE_URL

    engine = create_engine(DATABASE_URL)

    with Session(engine) as session:
        # Count records in canonical tables
        canonical_users = session.exec(select(CanonicalUser)).count()
        canonical_tasks = session.exec(select(CanonicalTask)).count()

        # Count records in legacy tables
        legacy_users = session.exec(select(LegacyUser)).count()
        legacy_todos = session.exec(select(LegacyTodo)).count()

        print(f"  Legacy users: {legacy_users}")
        print(f"  Legacy todos: {legacy_todos}")
        print(f"  Canonical users: {canonical_users}")
        print(f"  Canonical tasks: {canonical_tasks}")

        # Sample verification - get first canonical user and their tasks
        if canonical_users > 0:
            sample_user = session.exec(select(CanonicalUser).limit(1)).first()
            if sample_user:
                print(f"  Sample user: {sample_user.username} ({str(sample_user.id)[:8]}...)")

                # Check if user has associated tasks
                user_tasks = session.exec(
                    select(CanonicalTask).where(CanonicalTask.user_id == sample_user.id)
                ).count()
                print(f"  Tasks for this user: {user_tasks}")

        print("  Migration verification completed!")


if __name__ == "__main__":
    print("Database Migration Tool")
    print("=" * 50)

    try:
        migrate_database()
        verify_migration()
        print("\n✅ Database migration completed successfully!")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure you're running this from the correct directory.")
        print("Run this script from the root directory: python migrate_database.py")
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        import traceback
        traceback.print_exc()