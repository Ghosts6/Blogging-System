import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from fastapi.testclient import TestClient

User = get_user_model()


@pytest.fixture
def mock_celery_tasks():
    """Mock all Celery tasks to run synchronously in tests."""
    with patch('service.tasks.send_comment_notification_email.delay') as mock_task:
        # Make the mock return immediately
        mock_task.return_value = None
        yield mock_task


@pytest.fixture
def test_user(db):
    """Create a test user for authentication tests."""
    # Delete existing user if it exists (from previous test runs with --reuse-db)
    User.objects.filter(username="testuser").delete()
    
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpassword",
        first_name="test",
        last_name="user",
        is_staff=False,
        is_superuser=False,
        is_active=True,
    )
    return user


@pytest.fixture
def fastapi_app_fixture(db):
    """Import fastapi_app after Django settings and database are configured by pytest-django."""
    # Ensure test database connection is established before importing FastAPI
    from django.db import connections
    connections['default'].ensure_connection()
    
    from fastapi_app import app as fastapi_app
    return fastapi_app


@pytest.fixture
def client(fastapi_app_fixture):
    """Create a FastAPI test client."""
    return TestClient(fastapi_app_fixture)


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    pass
