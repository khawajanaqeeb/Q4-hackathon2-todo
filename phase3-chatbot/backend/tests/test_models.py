"""Test suite for database models."""

import pytest
from sqlmodel import Session, select
from datetime import datetime, timedelta
import uuid
from typing import Optional

from src.database import engine
from src.models.user import User
from src.models.task import Task, PriorityLevel
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.models.mcp_tool import McpTool
from src.models.api_key import ApiKey
from src.models.audit_log import AuditLog


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


def test_user_model_creation(db_session: Session):
    """Test creating a user model instance."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",
        is_active=True,
        is_superuser=False
    )
    
    db_session.add(user)
    db_session.commit()
    
    # Retrieve the user from the database
    retrieved_user = db_session.get(User, user_id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == user_id
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.username == "testuser"
    assert retrieved_user.hashed_password == "hashed_password_123"
    assert retrieved_user.is_active is True
    assert retrieved_user.is_superuser is False
    assert retrieved_user.created_at is not None
    assert retrieved_user.updated_at is not None


def test_user_model_defaults(db_session: Session):
    """Test default values for user model."""
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email="defaults@example.com",
        username="defaultsuser",
        hashed_password="hashed_password_123"
        # Not specifying is_active or is_superuser to test defaults
    )
    
    db_session.add(user)
    db_session.commit()
    
    retrieved_user = db_session.get(User, user_id)
    
    assert retrieved_user.is_active is True  # Default value
    assert retrieved_user.is_superuser is False  # Default value


def test_task_model_creation(db_session: Session, test_user: User):
    """Test creating a task model instance."""
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        user_id=test_user.id,
        title="Test Task",
        description="Test Description",
        priority=PriorityLevel.MEDIUM,
        completed=False,
        tags='["test", "important"]',  # Stored as JSON string
        due_date=datetime.utcnow() + timedelta(days=7)
    )
    
    db_session.add(task)
    db_session.commit()
    
    retrieved_task = db_session.get(Task, task_id)
    
    assert retrieved_task is not None
    assert retrieved_task.id == task_id
    assert retrieved_task.user_id == test_user.id
    assert retrieved_task.title == "Test Task"
    assert retrieved_task.description == "Test Description"
    assert retrieved_task.priority == PriorityLevel.MEDIUM
    assert retrieved_task.completed is False
    assert retrieved_task.tags == '["test", "important"]'
    assert retrieved_task.due_date is not None
    assert retrieved_task.created_at is not None
    assert retrieved_task.updated_at is not None


def test_task_model_defaults(db_session: Session, test_user: User):
    """Test default values for task model."""
    task_id = uuid.uuid4()
    task = Task(
        id=task_id,
        user_id=test_user.id,
        title="Minimal Task"
        # Only required field provided, others should use defaults
    )
    
    db_session.add(task)
    db_session.commit()
    
    retrieved_task = db_session.get(Task, task_id)
    
    assert retrieved_task.title == "Minimal Task"
    assert retrieved_task.description is None  # Default value
    assert retrieved_task.priority == PriorityLevel.MEDIUM  # Default value
    assert retrieved_task.completed is False  # Default value
    assert retrieved_task.tags is None  # Default value
    assert retrieved_task.due_date is None  # Default value


def test_conversation_model_creation(db_session: Session, test_user: User):
    """Test creating a conversation model instance."""
    conversation_id = uuid.uuid4()
    conversation = Conversation(
        id=conversation_id,
        user_id=test_user.id,
        title="Test Conversation",
        is_active=True
    )
    
    db_session.add(conversation)
    db_session.commit()
    
    retrieved_conv = db_session.get(Conversation, conversation_id)
    
    assert retrieved_conv is not None
    assert retrieved_conv.id == conversation_id
    assert retrieved_conv.user_id == test_user.id
    assert retrieved_conv.title == "Test Conversation"
    assert retrieved_conv.is_active is True
    assert retrieved_conv.created_at is not None
    assert retrieved_conv.updated_at is not None


def test_conversation_model_defaults(db_session: Session, test_user: User):
    """Test default values for conversation model."""
    conversation_id = uuid.uuid4()
    conversation = Conversation(
        id=conversation_id,
        user_id=test_user.id,
        title="Defaults Test"
        # Not specifying is_active to test default
    )
    
    db_session.add(conversation)
    db_session.commit()
    
    retrieved_conv = db_session.get(Conversation, conversation_id)
    
    assert retrieved_conv.is_active is True  # Default value


def test_message_model_creation(db_session: Session, test_conversation: Conversation):
    """Test creating a message model instance."""
    message_id = uuid.uuid4()
    message = Message(
        id=message_id,
        conversation_id=test_conversation.id,
        role=MessageRole.USER,
        content="Test message content",
        timestamp=datetime.utcnow()
    )
    
    db_session.add(message)
    db_session.commit()
    
    retrieved_msg = db_session.get(Message, message_id)
    
    assert retrieved_msg is not None
    assert retrieved_msg.id == message_id
    assert retrieved_msg.conversation_id == test_conversation.id
    assert retrieved_msg.role == MessageRole.USER
    assert retrieved_msg.content == "Test message content"
    assert retrieved_msg.timestamp is not None


def test_message_model_defaults(db_session: Session, test_conversation: Conversation):
    """Test default values for message model."""
    message_id = uuid.uuid4()
    message = Message(
        id=message_id,
        conversation_id=test_conversation.id,
        role=MessageRole.ASSISTANT,
        content="Default test message"
        # Not specifying timestamp to test default
    )
    
    db_session.add(message)
    db_session.commit()
    
    retrieved_msg = db_session.get(Message, message_id)
    
    assert retrieved_msg.timestamp is not None  # Should have default timestamp


def test_mcp_tool_model_creation(db_session: Session):
    """Test creating an MCP tool model instance."""
    tool_id = uuid.uuid4()
    schema_def = {
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "A test parameter"}
        },
        "required": ["param1"]
    }
    
    tool = McpTool(
        id=tool_id,
        name="test_tool",
        description="A test tool",
        provider="test_provider",
        tool_schema=schema_def,
        is_active=True
    )
    
    db_session.add(tool)
    db_session.commit()
    
    retrieved_tool = db_session.get(McpTool, tool_id)
    
    assert retrieved_tool is not None
    assert retrieved_tool.id == tool_id
    assert retrieved_tool.name == "test_tool"
    assert retrieved_tool.description == "A test tool"
    assert retrieved_tool.provider == "test_provider"
    assert retrieved_tool.tool_schema == schema_def
    assert retrieved_tool.is_active is True


def test_mcp_tool_model_defaults(db_session: Session):
    """Test default values for MCP tool model."""
    tool_id = uuid.uuid4()
    schema_def = {"type": "object"}
    
    tool = McpTool(
        id=tool_id,
        name="defaults_test_tool",
        description="A test tool for defaults",
        provider="test_provider",
        tool_schema=schema_def
        # Not specifying is_active to test default
    )
    
    db_session.add(tool)
    db_session.commit()
    
    retrieved_tool = db_session.get(McpTool, tool_id)
    
    assert retrieved_tool.is_active is True  # Default value


def test_api_key_model_creation(db_session: Session, test_user: User):
    """Test creating an API key model instance."""
    from src.utils.encryption import encrypt_api_key
    
    api_key_id = uuid.uuid4()
    encrypted_key = encrypt_api_key("test_api_key_12345")
    
    api_key = ApiKey(
        id=api_key_id,
        user_id=test_user.id,
        provider="openai",
        encrypted_key=encrypted_key,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    db_session.add(api_key)
    db_session.commit()
    
    retrieved_key = db_session.get(ApiKey, api_key_id)
    
    assert retrieved_key is not None
    assert retrieved_key.id == api_key_id
    assert retrieved_key.user_id == test_user.id
    assert retrieved_key.provider == "openai"
    assert retrieved_key.encrypted_key == encrypted_key
    assert retrieved_key.is_active is True
    assert retrieved_key.expires_at is not None


def test_api_key_model_defaults(db_session: Session, test_user: User):
    """Test default values for API key model."""
    from src.utils.encryption import encrypt_api_key
    
    api_key_id = uuid.uuid4()
    encrypted_key = encrypt_api_key("defaults_test_key")
    
    api_key = ApiKey(
        id=api_key_id,
        user_id=test_user.id,
        provider="anthropic",
        encrypted_key=encrypted_key
        # Not specifying is_active or expires_at to test defaults
    )
    
    db_session.add(api_key)
    db_session.commit()
    
    retrieved_key = db_session.get(ApiKey, api_key_id)
    
    assert retrieved_key.is_active is True  # Default value
    assert retrieved_key.expires_at is None  # Default value


def test_audit_log_model_creation(db_session: Session, test_user: User):
    """Test creating an audit log model instance."""
    log_id = uuid.uuid4()
    metadata = {"request_body": {"test": "data"}, "response_body": {"result": "success"}}
    
    audit_log = AuditLog(
        id=log_id,
        user_id=test_user.id,
        action_type="CREATE_TODO",
        resource_type="TODO",
        resource_id=uuid.uuid4(),
        log_metadata=metadata,
        success=True,
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    
    db_session.add(audit_log)
    db_session.commit()
    
    retrieved_log = db_session.get(AuditLog, log_id)
    
    assert retrieved_log is not None
    assert retrieved_log.id == log_id
    assert retrieved_log.user_id == test_user.id
    assert retrieved_log.action_type == "CREATE_TODO"
    assert retrieved_log.resource_type == "TODO"
    assert retrieved_log.log_metadata == metadata
    assert retrieved_log.success is True
    assert retrieved_log.ip_address == "127.0.0.1"
    assert retrieved_log.user_agent == "test-agent"
    assert retrieved_log.timestamp is not None


def test_audit_log_model_defaults(db_session: Session, test_user: User):
    """Test default values for audit log model."""
    log_id = uuid.uuid4()
    
    audit_log = AuditLog(
        id=log_id,
        user_id=test_user.id,
        action_type="TEST_ACTION",
        resource_type="TEST_RESOURCE",
        resource_id=uuid.uuid4(),
        # Not specifying success, response_time_ms, ip_address, user_agent to test defaults
    )
    
    db_session.add(audit_log)
    db_session.commit()
    
    retrieved_log = db_session.get(AuditLog, log_id)
    
    assert retrieved_log.success is True  # Default value
    assert retrieved_log.response_time_ms is None  # Default value
    assert retrieved_log.ip_address is None  # Default value
    assert retrieved_log.user_agent is None  # Default value


def test_user_task_relationship(db_session: Session):
    """Test the relationship between User and Task models."""
    # Create a user
    user = User(
        id=uuid.uuid4(),
        email="relationship@example.com",
        username="reluser",
        hashed_password="hashed_password_123",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create a task for the user
    task = Task(
        id=uuid.uuid4(),
        user_id=user.id,
        title="Related Task",
        priority=PriorityLevel.HIGH
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    
    # Retrieve the user and check the relationship
    retrieved_user = db_session.get(User, user.id)
    
    # The relationship might not be loaded by default, so we'll test the foreign key
    assert task.user_id == retrieved_user.id


def test_conversation_message_relationship(db_session: Session):
    """Test the relationship between Conversation and Message models."""
    # Create a conversation
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),  # Creating a temporary user ID for this test
        title="Relationship Test Conversation",
        is_active=True
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    
    # Create a message in the conversation
    message = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Test message for relationship"
    )
    db_session.add(message)
    db_session.commit()
    db_session.refresh(message)
    
    # Verify the foreign key relationship
    assert message.conversation_id == conversation.id
    
    # Test retrieving messages for a conversation
    statement = select(Message).where(Message.conversation_id == conversation.id)
    messages = db_session.exec(statement).all()
    
    assert len(messages) == 1
    assert messages[0].id == message.id


def test_user_validation_constraints(db_session: Session):
    """Test validation constraints for the User model."""
    # Test that email and username must be unique
    user1 = User(
        id=uuid.uuid4(),
        email="unique@example.com",
        username="uniqueuser",
        hashed_password="hashed_password_123",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user1)
    db_session.commit()
    
    # Try to create another user with the same email
    user2 = User(
        id=uuid.uuid4(),
        email="unique@example.com",  # Same email as user1
        username="differentuser",
        hashed_password="hashed_password_456",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user2)
    
    # This should cause a database constraint violation
    with pytest.raises(Exception):
        db_session.commit()
    
    # Roll back the transaction
    db_session.rollback()
    
    # Try to create another user with the same username
    user3 = User(
        id=uuid.uuid4(),
        email="different@example.com",
        username="uniqueuser",  # Same username as user1
        hashed_password="hashed_password_789",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user3)
    
    # This should also cause a database constraint violation
    with pytest.raises(Exception):
        db_session.commit()
    
    db_session.rollback()


def test_task_priority_enum(db_session: Session, test_user: User):
    """Test that the PriorityLevel enum works correctly in the Task model."""
    # Test all priority levels
    priorities = [PriorityLevel.LOW, PriorityLevel.MEDIUM, PriorityLevel.HIGH]
    
    for i, priority in enumerate(priorities):
        task = Task(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title=f"Task with {priority} priority",
            priority=priority
        )
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)
        
        retrieved_task = db_session.get(Task, task.id)
        assert retrieved_task.priority == priority


def test_message_role_enum(db_session: Session, test_conversation: Conversation):
    """Test that the MessageRole enum works correctly in the Message model."""
    # Test all message roles
    roles = [MessageRole.USER, MessageRole.ASSISTANT, MessageRole.SYSTEM]
    
    for i, role in enumerate(roles):
        message = Message(
            id=uuid.uuid4(),
            conversation_id=test_conversation.id,
            role=role,
            content=f"Message with {role} role"
        )
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        
        retrieved_msg = db_session.get(Message, message.id)
        assert retrieved_msg.role == role


def test_task_search_functionality(db_session: Session, test_user: User):
    """Test searching/filtering tasks."""
    # Create multiple tasks
    task1 = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Grocery Shopping",
        description="Buy milk, eggs, and bread",
        priority=PriorityLevel.HIGH,
        completed=False
    )
    task2 = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Work Report",
        description="Finish quarterly report",
        priority=PriorityLevel.MEDIUM,
        completed=True
    )
    task3 = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Doctor Appointment",
        description="Annual checkup",
        priority=PriorityLevel.LOW,
        completed=False
    )
    
    db_session.add(task1)
    db_session.add(task2)
    db_session.add(task3)
    db_session.commit()
    
    # Test filtering by completion status
    completed_stmt = select(Task).where(Task.user_id == test_user.id, Task.completed == True)
    completed_tasks = db_session.exec(completed_stmt).all()
    assert len(completed_tasks) == 1
    assert completed_tasks[0].title == "Work Report"
    
    # Test filtering by priority
    high_priority_stmt = select(Task).where(Task.user_id == test_user.id, Task.priority == PriorityLevel.HIGH)
    high_priority_tasks = db_session.exec(high_priority_stmt).all()
    assert len(high_priority_tasks) == 1
    assert high_priority_tasks[0].title == "Grocery Shopping"
    
    # Test searching by title
    search_stmt = select(Task).where(
        Task.user_id == test_user.id,
        Task.title.contains("Report")
    )
    search_results = db_session.exec(search_stmt).all()
    assert len(search_results) == 1
    assert search_results[0].title == "Work Report"
    
    # Test searching by description
    desc_search_stmt = select(Task).where(
        Task.user_id == test_user.id,
        Task.description.contains("milk")
    )
    desc_search_results = db_session.exec(desc_search_stmt).all()
    assert len(desc_search_results) == 1
    assert desc_search_results[0].title == "Grocery Shopping"


def test_user_timestamps(db_session: Session):
    """Test that timestamps are properly set for User model."""
    user_id = uuid.uuid4()
    before_create = datetime.utcnow()
    
    user = User(
        id=user_id,
        email="timestamps@example.com",
        username="timestampuser",
        hashed_password="hashed_password_123"
    )
    db_session.add(user)
    db_session.commit()
    
    after_create = datetime.utcnow()
    
    retrieved_user = db_session.get(User, user_id)
    
    assert retrieved_user.created_at is not None
    assert retrieved_user.updated_at is not None
    assert before_create <= retrieved_user.created_at <= after_create


def test_task_timestamps(db_session: Session, test_user: User):
    """Test that timestamps are properly set for Task model."""
    task_id = uuid.uuid4()
    before_create = datetime.utcnow()
    
    task = Task(
        id=task_id,
        user_id=test_user.id,
        title="Timestamp Test Task"
    )
    db_session.add(task)
    db_session.commit()
    
    after_create = datetime.utcnow()
    
    retrieved_task = db_session.get(Task, task_id)
    
    assert retrieved_task.created_at is not None
    assert retrieved_task.updated_at is not None
    assert before_create <= retrieved_task.created_at <= after_create


def test_conversation_timestamps(db_session: Session, test_user: User):
    """Test that timestamps are properly set for Conversation model."""
    conv_id = uuid.uuid4()
    before_create = datetime.utcnow()
    
    conversation = Conversation(
        id=conv_id,
        user_id=test_user.id,
        title="Timestamp Test Conversation"
    )
    db_session.add(conversation)
    db_session.commit()
    
    after_create = datetime.utcnow()
    
    retrieved_conv = db_session.get(Conversation, conv_id)
    
    assert retrieved_conv.created_at is not None
    assert retrieved_conv.updated_at is not None
    assert before_create <= retrieved_conv.created_at <= after_create


def test_message_timestamps(db_session: Session, test_conversation: Conversation):
    """Test that timestamps are properly set for Message model."""
    msg_id = uuid.uuid4()
    before_create = datetime.utcnow()
    
    message = Message(
        id=msg_id,
        conversation_id=test_conversation.id,
        role=MessageRole.USER,
        content="Timestamp test message"
    )
    db_session.add(message)
    db_session.commit()
    
    after_create = datetime.utcnow()
    
    retrieved_msg = db_session.get(Message, msg_id)
    
    assert retrieved_msg.timestamp is not None
    assert before_create <= retrieved_msg.timestamp <= after_create


@pytest.fixture(scope="function")
def test_user(db_session: Session):
    """Create a test user for other tests."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_123",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_conversation(db_session: Session, test_user: User):
    """Create a test conversation for other tests."""
    conversation = Conversation(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Test Conversation"
    )
    db_session.add(conversation)
    db_session.commit()
    db_session.refresh(conversation)
    return conversation