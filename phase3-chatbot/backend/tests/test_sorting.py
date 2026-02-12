"""Test suite for task sorting, filtering, and listing behavior."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta

from src.models.task import Task, PriorityLevel


def _create_task(session, user_id, title, priority, completed=False, days_ago=0):
    """Helper to create tasks with varying timestamps."""
    task = Task(
        user_id=user_id,
        title=title,
        priority=priority,
        completed=completed,
        created_at=datetime.utcnow() - timedelta(days=days_ago),
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


class TestTaskSorting:
    """Tests that verify list ordering and filtering."""

    def test_list_returns_only_current_user_tasks(
        self,
        client: TestClient,
        test_user,
        test_user2,
        auth_headers,
        auth_headers2,
        session: Session,
    ):
        """Each user sees only their own tasks."""
        _create_task(session, test_user.id, "User1 Task", PriorityLevel.HIGH)
        _create_task(session, test_user2.id, "User2 Task", PriorityLevel.LOW)

        r1 = client.get("/api/todos/", headers=auth_headers)
        r2 = client.get("/api/todos/", headers=auth_headers2)

        titles1 = [t["title"] for t in r1.json()]
        titles2 = [t["title"] for t in r2.json()]

        assert "User1 Task" in titles1
        assert "User2 Task" not in titles1
        assert "User2 Task" in titles2
        assert "User1 Task" not in titles2

    def test_filter_by_completed_true(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Filter completed=true returns only completed tasks."""
        _create_task(session, test_user.id, "Done", PriorityLevel.LOW, completed=True)
        _create_task(session, test_user.id, "Not Done", PriorityLevel.LOW, completed=False)

        response = client.get("/api/todos/?completed=true", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(t["completed"] is True for t in data)
        titles = [t["title"] for t in data]
        assert "Done" in titles
        assert "Not Done" not in titles

    def test_filter_by_completed_false(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Filter completed=false returns only pending tasks."""
        _create_task(session, test_user.id, "Done2", PriorityLevel.LOW, completed=True)
        _create_task(session, test_user.id, "Pending", PriorityLevel.LOW, completed=False)

        response = client.get("/api/todos/?completed=false", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(t["completed"] is False for t in data)

    def test_filter_by_high_priority(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Filter priority=high returns only high priority tasks."""
        _create_task(session, test_user.id, "Urgent", PriorityLevel.HIGH)
        _create_task(session, test_user.id, "Normal", PriorityLevel.MEDIUM)
        _create_task(session, test_user.id, "Chill", PriorityLevel.LOW)

        response = client.get("/api/todos/?priority=high", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(t["priority"] == "high" for t in data)

    def test_filter_by_low_priority(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Filter priority=low returns only low priority tasks."""
        _create_task(session, test_user.id, "Someday", PriorityLevel.LOW)
        _create_task(session, test_user.id, "Important", PriorityLevel.HIGH)

        response = client.get("/api/todos/?priority=low", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(t["priority"] == "low" for t in data)

    def test_filter_combined_priority_and_completed(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Combining filters works correctly."""
        _create_task(session, test_user.id, "Done High", PriorityLevel.HIGH, completed=True)
        _create_task(session, test_user.id, "Pending High", PriorityLevel.HIGH, completed=False)
        _create_task(session, test_user.id, "Done Low", PriorityLevel.LOW, completed=True)

        response = client.get(
            "/api/todos/?priority=high&completed=true", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for t in data:
            assert t["priority"] == "high"
            assert t["completed"] is True

    def test_multiple_tasks_returned(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Multiple tasks are all returned in the list."""
        for i in range(5):
            _create_task(session, test_user.id, f"Task {i}", PriorityLevel.MEDIUM)

        response = client.get("/api/todos/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 5

    def test_empty_list_for_new_user(
        self, client: TestClient, test_user, auth_headers
    ):
        """New user with no tasks gets empty list."""
        response = client.get("/api/todos/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_without_auth_rejected(self, client: TestClient):
        """Listing tasks without auth returns 401."""
        response = client.get("/api/todos/")
        assert response.status_code == 401


class TestTaskCRUDFlow:
    """End-to-end create -> read -> update -> delete flow."""

    def test_full_crud_flow(
        self, client: TestClient, test_user, auth_headers, session: Session
    ):
        """Create a task, read it, update it, delete it."""
        # CREATE
        r = client.post(
            "/api/todos/",
            json={"title": "CRUD Task", "priority": "medium"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        task_id = r.json()["id"]

        # READ
        r = client.get("/api/todos/", headers=auth_headers)
        ids = [t["id"] for t in r.json()]
        assert task_id in ids

        # UPDATE
        r = client.put(
            f"/api/todos/{task_id}",
            json={"title": "CRUD Task Updated", "priority": "high"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["title"] == "CRUD Task Updated"
        assert r.json()["priority"] == "high"

        # TOGGLE COMPLETE
        r = client.patch(f"/api/todos/{task_id}/toggle", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["completed"] is True

        # DELETE
        r = client.delete(f"/api/todos/{task_id}", headers=auth_headers)
        assert r.status_code == 200

        # VERIFY DELETED
        r = client.get("/api/todos/", headers=auth_headers)
        ids = [t["id"] for t in r.json()]
        assert task_id not in ids
