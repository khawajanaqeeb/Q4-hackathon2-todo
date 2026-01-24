"""Comprehensive tests for todo CRUD operations and user isolation.

This test module verifies:
- All todo CRUD endpoints (create, read, update, delete, toggle)
- User isolation security (users can only access their own todos)
- Search, filter, and sort functionality
- Pagination
- Edge cases and error handling
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


# ============================================================================
# CREATE TODO TESTS
# ============================================================================

def test_create_todo_success(client: TestClient, auth_headers: dict):
    """Test creating a todo with valid authentication."""
    response = client.post(
        "/todos/",
        headers=auth_headers,
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high",
            "tags": ["shopping", "urgent"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["priority"] == "high"
    assert data["tags"] == ["shopping", "urgent"]
    assert data["completed"] is False
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_todo_minimal(client: TestClient, auth_headers: dict):
    """Test creating a todo with only required fields."""
    response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Simple task"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Simple task"
    assert data["description"] is None
    assert data["priority"] == "medium"  # Default
    assert data["tags"] == []
    assert data["completed"] is False


def test_create_todo_unauthorized(client: TestClient):
    """Test creating a todo without authentication fails."""
    response = client.post(
        "/todos/",
        json={"title": "Unauthorized task"}
    )

    assert response.status_code == 401


def test_create_todo_empty_title(client: TestClient, auth_headers: dict):
    """Test creating a todo with empty title fails validation."""
    response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "   "}  # Whitespace only
    )

    assert response.status_code == 422


def test_create_todo_too_many_tags(client: TestClient, auth_headers: dict):
    """Test creating a todo with more than 10 tags fails."""
    response = client.post(
        "/todos/",
        headers=auth_headers,
        json={
            "title": "Task with too many tags",
            "tags": [f"tag{i}" for i in range(11)]  # 11 tags
        }
    )

    assert response.status_code == 422


# ============================================================================
# GET TODOS TESTS
# ============================================================================

def test_get_todos_empty_list(client: TestClient, auth_headers: dict):
    """Test getting todos returns empty list when user has no todos."""
    response = client.get("/todos/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_todos_list(client: TestClient, auth_headers: dict):
    """Test getting todos returns all user's todos."""
    # Create 3 todos
    for i in range(3):
        client.post(
            "/todos/",
            headers=auth_headers,
            json={"title": f"Task {i+1}"}
        )

    response = client.get("/todos/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # Should be ordered by created_at desc (most recent first)
    assert data[0]["title"] == "Task 3"
    assert data[1]["title"] == "Task 2"
    assert data[2]["title"] == "Task 1"


def test_get_todos_unauthorized(client: TestClient):
    """Test getting todos without authentication fails."""
    response = client.get("/todos/")

    assert response.status_code == 401


def test_get_todos_filter_by_completed(client: TestClient, auth_headers: dict):
    """Test filtering todos by completion status."""
    # Create completed and pending todos
    response1 = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Completed task", "completed": False}
    )
    todo1_id = response1.json()["id"]

    # Toggle to completed
    client.patch(f"/todos/{todo1_id}/toggle", headers=auth_headers)

    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Pending task"}
    )

    # Get only completed
    response = client.get("/todos/?completed=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Completed task"
    assert data[0]["completed"] is True

    # Get only pending
    response = client.get("/todos/?completed=false", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Pending task"
    assert data[0]["completed"] is False


def test_get_todos_filter_by_priority(client: TestClient, auth_headers: dict):
    """Test filtering todos by priority level."""
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Low priority task", "priority": "low"}
    )
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "High priority task", "priority": "high"}
    )

    # Get only high priority
    response = client.get("/todos/?priority=high", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "High priority task"
    assert data[0]["priority"] == "high"


def test_get_todos_search(client: TestClient, auth_headers: dict):
    """Test searching todos by title and description."""
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Buy groceries", "description": "Milk and eggs"}
    )
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Pay bills", "description": "Electricity and water"}
    )

    # Search in title
    response = client.get("/todos/?search=groceries", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "groceries" in data[0]["title"]

    # Search in description
    response = client.get("/todos/?search=Electricity", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "bills" in data[0]["title"]


def test_get_todos_pagination(client: TestClient, auth_headers: dict):
    """Test pagination with skip and limit parameters."""
    # Create 5 todos
    for i in range(5):
        client.post(
            "/todos/",
            headers=auth_headers,
            json={"title": f"Task {i+1}"}
        )

    # Get first 2
    response = client.get("/todos/?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Get next 2
    response = client.get("/todos/?skip=2&limit=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


# ============================================================================
# UPDATE TODO TESTS
# ============================================================================

def test_update_todo_success(client: TestClient, auth_headers: dict):
    """Test updating a todo with valid authentication."""
    # Create a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Original title", "priority": "low"}
    )
    todo_id = create_response.json()["id"]

    # Update the todo
    update_response = client.put(
        f"/todos/{todo_id}",
        headers=auth_headers,
        json={
            "title": "Updated title",
            "priority": "high",
            "completed": True
        }
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated title"
    assert data["priority"] == "high"
    assert data["completed"] is True


def test_update_todo_partial(client: TestClient, auth_headers: dict):
    """Test partial update (only some fields)."""
    # Create a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Original", "description": "Original description"}
    )
    todo_id = create_response.json()["id"]

    # Update only title
    update_response = client.put(
        f"/todos/{todo_id}",
        headers=auth_headers,
        json={"title": "Updated title only"}
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Updated title only"
    assert data["description"] == "Original description"  # Unchanged


def test_update_todo_not_found(client: TestClient, auth_headers: dict):
    """Test updating a non-existent todo returns 404."""
    response = client.put(
        "/todos/99999",
        headers=auth_headers,
        json={"title": "Updated"}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_todo_unauthorized(client: TestClient):
    """Test updating a todo without authentication fails."""
    response = client.put(
        "/todos/1",
        json={"title": "Updated"}
    )

    assert response.status_code == 401


# ============================================================================
# DELETE TODO TESTS
# ============================================================================

def test_delete_todo_success(client: TestClient, auth_headers: dict):
    """Test deleting a todo with valid authentication."""
    # Create a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "To be deleted"}
    )
    todo_id = create_response.json()["id"]

    # Delete the todo
    delete_response = client.delete(
        f"/todos/{todo_id}",
        headers=auth_headers
    )

    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"].lower()

    # Verify it's actually deleted
    get_response = client.get("/todos/", headers=auth_headers)
    todos = get_response.json()
    assert len(todos) == 0


def test_delete_todo_not_found(client: TestClient, auth_headers: dict):
    """Test deleting a non-existent todo returns 404."""
    response = client.delete("/todos/99999", headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_todo_unauthorized(client: TestClient):
    """Test deleting a todo without authentication fails."""
    response = client.delete("/todos/1")

    assert response.status_code == 401


# ============================================================================
# TOGGLE COMPLETION TESTS
# ============================================================================

def test_toggle_todo_completion(client: TestClient, auth_headers: dict):
    """Test toggling todo completion status."""
    # Create a todo (default: not completed)
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "Toggle test"}
    )
    todo_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    # Toggle to completed
    toggle_response1 = client.patch(
        f"/todos/{todo_id}/toggle",
        headers=auth_headers
    )
    assert toggle_response1.status_code == 200
    assert toggle_response1.json()["completed"] is True

    # Toggle back to not completed
    toggle_response2 = client.patch(
        f"/todos/{todo_id}/toggle",
        headers=auth_headers
    )
    assert toggle_response2.status_code == 200
    assert toggle_response2.json()["completed"] is False


def test_toggle_todo_not_found(client: TestClient, auth_headers: dict):
    """Test toggling a non-existent todo returns 404."""
    response = client.patch("/todos/99999/toggle", headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_toggle_todo_unauthorized(client: TestClient):
    """Test toggling a todo without authentication fails."""
    response = client.patch("/todos/1/toggle")

    assert response.status_code == 401


# ============================================================================
# USER ISOLATION TESTS (CRITICAL SECURITY)
# ============================================================================

def test_user_isolation_get_todos(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """SECURITY: Users can only see their own todos, not other users' todos."""
    # User 1 creates 2 todos
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "User 1 Task 1"}
    )
    client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "User 1 Task 2"}
    )

    # User 2 creates 1 todo
    client.post(
        "/todos/",
        headers=auth_headers_user2,
        json={"title": "User 2 Task 1"}
    )

    # User 1 should only see their 2 todos
    response1 = client.get("/todos/", headers=auth_headers)
    assert response1.status_code == 200
    todos1 = response1.json()
    assert len(todos1) == 2
    assert all("User 1" in todo["title"] for todo in todos1)

    # User 2 should only see their 1 todo
    response2 = client.get("/todos/", headers=auth_headers_user2)
    assert response2.status_code == 200
    todos2 = response2.json()
    assert len(todos2) == 1
    assert "User 2" in todos2[0]["title"]


def test_user_isolation_update_other_user_todo(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """SECURITY: Users cannot update other users' todos."""
    # User 1 creates a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "User 1 Task"}
    )
    todo_id = create_response.json()["id"]

    # User 2 tries to update User 1's todo - should be forbidden
    update_response = client.put(
        f"/todos/{todo_id}",
        headers=auth_headers_user2,
        json={"title": "Hacked!"}
    )

    assert update_response.status_code == 403
    assert "not authorized" in update_response.json()["detail"].lower()

    # Verify the todo was NOT updated
    get_response = client.get("/todos/", headers=auth_headers)
    todos = get_response.json()
    assert todos[0]["title"] == "User 1 Task"  # Original title preserved


def test_user_isolation_delete_other_user_todo(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """SECURITY: Users cannot delete other users' todos."""
    # User 1 creates a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "User 1 Task"}
    )
    todo_id = create_response.json()["id"]

    # User 2 tries to delete User 1's todo - should be forbidden
    delete_response = client.delete(
        f"/todos/{todo_id}",
        headers=auth_headers_user2
    )

    assert delete_response.status_code == 403
    assert "not authorized" in delete_response.json()["detail"].lower()

    # Verify the todo was NOT deleted
    get_response = client.get("/todos/", headers=auth_headers)
    todos = get_response.json()
    assert len(todos) == 1
    assert todos[0]["title"] == "User 1 Task"


def test_user_isolation_toggle_other_user_todo(
    client: TestClient,
    auth_headers: dict,
    auth_headers_user2: dict
):
    """SECURITY: Users cannot toggle other users' todos."""
    # User 1 creates a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"title": "User 1 Task"}
    )
    todo_id = create_response.json()["id"]

    # User 2 tries to toggle User 1's todo - should be forbidden
    toggle_response = client.patch(
        f"/todos/{todo_id}/toggle",
        headers=auth_headers_user2
    )

    assert toggle_response.status_code == 403
    assert "not authorized" in toggle_response.json()["detail"].lower()

    # Verify the todo completion status was NOT changed
    get_response = client.get("/todos/", headers=auth_headers)
    todos = get_response.json()
    assert todos[0]["completed"] is False  # Still not completed


# ============================================================================
# COMBINED FILTERS AND EDGE CASES
# ============================================================================

def test_combined_filters(client: TestClient, auth_headers: dict):
    """Test combining multiple filters (priority + completed + search)."""
    # Create diverse todos
    client.post(
        "/todos/",
        headers=auth_headers,
        json={
            "title": "Important shopping",
            "priority": "high",
            "completed": False
        }
    )
    client.post(
        "/todos/",
        headers=auth_headers,
        json={
            "title": "Regular shopping",
            "priority": "medium",
            "completed": True
        }
    )
    client.post(
        "/todos/",
        headers=auth_headers,
        json={
            "title": "Important meeting",
            "priority": "high",
            "completed": False
        }
    )

    # Filter: high priority + not completed + search "Important"
    response = client.get(
        "/todos/?priority=high&completed=false&search=Important",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(todo["priority"] == "high" for todo in data)
    assert all(todo["completed"] is False for todo in data)
    assert all("Important" in todo["title"] for todo in data)


def test_pagination_limits(client: TestClient, auth_headers: dict):
    """Test pagination edge cases."""
    # Create 5 todos
    for i in range(5):
        client.post(
            "/todos/",
            headers=auth_headers,
            json={"title": f"Task {i+1}"}
        )

    # Test limit=0 is invalid (should use minimum 1)
    response = client.get("/todos/?limit=0", headers=auth_headers)
    assert response.status_code == 422

    # Test limit > 100 is invalid (maximum is 100)
    response = client.get("/todos/?limit=101", headers=auth_headers)
    assert response.status_code == 422

    # Test skip beyond total count returns empty list
    response = client.get("/todos/?skip=100", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0
