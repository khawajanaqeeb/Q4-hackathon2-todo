"""Test suite for todo endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import uuid4
import uuid
from datetime import datetime

from src.main import app
from src.database import get_session, engine
from src.models.user import User
from src.models.task import Task, PriorityLevel
from src.dependencies.auth import get_current_user
from src.config import settings
from src.utils.security import create_access_token


@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=pwd_context.hash("testpassword123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authentication headers for test user."""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {access_token}"}


def test_create_todo_success(client: TestClient, test_user, auth_headers: dict):
    """Test successful creation of a todo."""
    response = client.post(
        "/api/todos/",
        json={
            "title": "Test Todo",
            "description": "Test Description",
            "priority": "medium",
            "tags": ["test", "important"]
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test Description"
    assert data["priority"] == "medium"
    assert data["tags"] == ["test", "important"]
    assert "id" in data
    assert "created_at" in data


def test_create_todo_minimal_fields(client: TestClient, test_user, auth_headers: dict):
    """Test creating a todo with minimal required fields only."""
    response = client.post(
        "/api/todos/",
        json={
            "title": "Minimal Todo"
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Minimal Todo"
    assert data["description"] is None
    assert data["priority"] == "medium"  # Default value
    assert data["tags"] is None  # Default value
    assert data["completed"] is False  # Default value


def test_create_todo_with_all_fields(client: TestClient, test_user, auth_headers: dict):
    """Test creating a todo with all fields specified."""
    from datetime import datetime
    due_date = datetime.now().strftime("%Y-%m-%d")
    
    response = client.post(
        "/api/todos/",
        json={
            "title": "Complete Todo",
            "description": "Detailed description",
            "completed": False,
            "priority": "high",
            "tags": ["work", "urgent"],
            "due_date": due_date
        },
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Complete Todo"
    assert data["description"] == "Detailed description"
    assert data["completed"] is False
    assert data["priority"] == "high"
    assert data["tags"] == ["work", "urgent"]
    assert data["due_date"] is not None


def test_get_todos_empty_list(client: TestClient, test_user, auth_headers: dict):
    """Test getting todos when none exist."""
    response = client.get("/api/todos/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_todos_with_existing_data(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting todos when some exist."""
    # Create a test task directly in the database
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Existing Task",
        description="Existing Description",
        priority=PriorityLevel.MEDIUM,
        completed=False,
        tags='["existing", "test"]'
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.get("/api/todos/", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Find our task in the response
    our_task = next((item for item in data if item["id"] == str(task.id)), None)
    assert our_task is not None
    assert our_task["title"] == "Existing Task"
    assert our_task["description"] == "Existing Description"


def test_get_todos_with_filters(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test getting todos with filters applied."""
    # Create test tasks with different properties
    task1 = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Completed Task",
        priority=PriorityLevel.HIGH,
        completed=True
    )
    task2 = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Pending Task",
        priority=PriorityLevel.LOW,
        completed=False
    )
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()
    
    # Test completed filter
    response = client.get("/api/todos/?completed=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    completed_tasks = [t for t in data if t["completed"]]
    assert len(completed_tasks) >= 1
    
    # Test priority filter
    response = client.get("/api/todos/?priority=high", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    high_priority_tasks = [t for t in data if t["priority"] == "high"]
    assert len(high_priority_tasks) >= 1


def test_update_todo_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test successful update of a todo."""
    # Create a task to update
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Original Title",
        description="Original Description",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "priority": "high",
        "completed": True,
        "tags": ["updated", "test"]
    }
    
    response = client.put(f"/api/todos/{task.id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated Description"
    assert data["priority"] == "high"
    assert data["completed"] is True
    assert data["tags"] == ["updated", "test"]


def test_update_todo_partial_fields(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test updating only some fields of a todo."""
    # Create a task to update
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Original Title",
        description="Original Description",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    update_data = {
        "title": "Updated Title Only"
    }
    
    response = client.put(f"/api/todos/{task.id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title Only"
    # Other fields should remain unchanged
    assert data["description"] == "Original Description"  # Should remain the same
    assert data["priority"] == "medium"  # Should remain the same
    assert data["completed"] is False  # Should remain the same


def test_update_todo_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test updating a non-existent todo."""
    fake_id = str(uuid.uuid4())
    update_data = {"title": "Updated Title"}
    
    response = client.put(f"/api/todos/{fake_id}", json=update_data, headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_update_todo_not_authorized(client: TestClient, db_session: Session, auth_headers: dict):
    """Test updating a todo that belongs to another user."""
    # Create a different user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    other_user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        username="otheruser",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(other_user)
    
    # Create a task belonging to the other user
    task = Task(
        id=uuid.uuid4(),
        user_id=other_user.id,
        title="Other User's Task",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    update_data = {"title": "Attempted Update"}
    
    response = client.put(f"/api/todos/{task.id}", json=update_data, headers=auth_headers)
    
    # Should return 403 Forbidden since the task belongs to another user
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_todo_success(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test successful deletion of a todo."""
    # Create a task to delete
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Task to Delete",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.delete(f"/api/todos/{task.id}", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "deleted" in data["message"].lower()
    
    # Verify the task was actually deleted
    statement = select(Task).where(Task.id == task.id)
    deleted_task = db_session.exec(statement).first()
    assert deleted_task is None


def test_delete_todo_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test deleting a non-existent todo."""
    fake_id = str(uuid.uuid4())
    
    response = client.delete(f"/api/todos/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_todo_not_authorized(client: TestClient, db_session: Session, auth_headers: dict):
    """Test deleting a todo that belongs to another user."""
    # Create a different user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    other_user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        username="otheruser",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(other_user)
    
    # Create a task belonging to the other user
    task = Task(
        id=uuid.uuid4(),
        user_id=other_user.id,
        title="Other User's Task",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.delete(f"/api/todos/{task.id}", headers=auth_headers)
    
    # Should return 403 Forbidden since the task belongs to another user
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_toggle_todo_completion(client: TestClient, test_user, auth_headers: dict, db_session: Session):
    """Test toggling the completion status of a todo."""
    # Create a task to toggle
    task = Task(
        id=uuid.uuid4(),
        user_id=test_user.id,
        title="Toggle Task",
        priority=PriorityLevel.MEDIUM,
        completed=False  # Initially not completed
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.patch(f"/api/todos/{task.id}/toggle", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is True  # Should now be completed
    
    # Toggle again to make sure it works both ways
    response = client.patch(f"/api/todos/{task.id}/toggle", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["completed"] is False  # Should now be not completed


def test_toggle_todo_not_found(client: TestClient, test_user, auth_headers: dict):
    """Test toggling completion of a non-existent todo."""
    fake_id = str(uuid.uuid4())
    
    response = client.patch(f"/api/todos/{fake_id}/toggle", headers=auth_headers)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_toggle_todo_not_authorized(client: TestClient, db_session: Session, auth_headers: dict):
    """Test toggling completion of a todo that belongs to another user."""
    # Create a different user
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    other_user = User(
        id=uuid.uuid4(),
        email="other@example.com",
        username="otheruser",
        hashed_password=pwd_context.hash("password123"),
        is_active=True,
        is_superuser=False
    )
    db_session.add(other_user)
    
    # Create a task belonging to the other user
    task = Task(
        id=uuid.uuid4(),
        user_id=other_user.id,
        title="Other User's Task",
        priority=PriorityLevel.MEDIUM,
        completed=False
    )
    db_session.add(task)
    db_session.commit()
    
    response = client.patch(f"/api/todos/{task.id}/toggle", headers=auth_headers)
    
    # Should return 403 Forbidden since the task belongs to another user
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_unauthorized_access(client: TestClient):
    """Test that unauthorized access is properly rejected."""
    # Try to create a todo without authentication
    response = client.post(
        "/api/todos/",
        json={"title": "Unauthorized Todo"}
    )
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to get todos without authentication
    response = client.get("/api/todos/")
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Try to update a todo without authentication
    response = client.put("/api/todos/1", json={"title": "Updated"})
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data