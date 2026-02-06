"""Simple test to check database connection and conversation creation."""

from src.database import get_session
from src.models.conversation import Conversation
from src.models.user import User
from sqlmodel import select
import uuid

def test_db_connection():
    print("Testing database connection...")
    
    # Get a fresh session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Check if user exists
        user_id = uuid.UUID("c553fa23-f7f2-4269-906b-ced970ee6d70")
        user = session.get(User, user_id)
        
        if user:
            print(f"User found: {user.username}")
        else:
            print("User not found")
            return
        
        # Try to create a conversation
        from datetime import datetime
        conversation = Conversation(
            user_id=user_id,
            title="Test Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        print(f"Conversation created successfully: {conversation.id}")
        
        # Clean up
        session.delete(conversation)
        session.commit()
        print("Test completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        # Close the session
        try:
            next(session_gen)
        except StopIteration:
            pass

if __name__ == "__main__":
    test_db_connection()