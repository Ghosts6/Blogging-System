# conftest.py
import pytest
from django.contrib.auth import get_user_model
from fastapi.testclient import TestClient
from fastapi_app import app as fastapi_app

User = get_user_model()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        first_name="test",
        last_name="user",
        is_staff=False,
        is_superuser=False,
        is_active=True,
    )
    user.set_password("testpassword")
    user.save()
    return user

@pytest.fixture
def client():
    return TestClient(fastapi_app)
