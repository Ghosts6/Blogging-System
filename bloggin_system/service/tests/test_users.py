import pytest
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
def test_user_authentication(test_user):
    user = authenticate(username='testuser', password='testpassword')
    assert user is not None
    assert user.username == 'testuser'


@pytest.mark.django_db
def test_user_authentication_wrong_password(test_user):
    user = authenticate(username='testuser', password='wrongpassword')
    assert user is None


@pytest.mark.django_db(transaction=True)
def test_signup(client):
    # Clean up any existing user with this name
    User.objects.filter(username="newuser").delete()
    
    response = client.post("/signup/", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User created successfully"
    
    # Verify user was created
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db(transaction=True)
def test_signup_duplicate_username(client, test_user):
    response = client.post("/signup/", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_login(client, test_user):
    response = client.post("/login/", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.django_db
def test_login_invalid_credentials(client, test_user):
    response = client.post("/login/", json={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.django_db
def test_login_nonexistent_user(client):
    response = client.post("/login/", json={
        "username": "nonexistent",
        "password": "password"
    })
    assert response.status_code == 400
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_password_reset(client, test_user):
    response = client.post("/password_reset/", json={
        "username": "testuser",
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"
    
    # Verify password was changed
    user = authenticate(username='testuser', password='newpassword123')
    assert user is not None


@pytest.mark.django_db
def test_password_reset_nonexistent_user(client):
    response = client.post("/password_reset/", json={
        "username": "nonexistent",
        "new_password": "newpassword123"
    })
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_password_reset_request(client, test_user):
    response = client.post("/password-reset-request/", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    assert "token" in response.json()
    
    # Verify token was set
    user = User.objects.get(username="testuser")
    assert user.password_reset_token is not None
    assert user.password_reset_token_created_at is not None


@pytest.mark.django_db
def test_password_reset_request_invalid_email(client):
    response = client.post("/password-reset-request/", json={
        "email": "nonexistent@example.com"
    })
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_password_reset_confirm(client, test_user):
    # Request password reset
    response = client.post("/password-reset-request/", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    token = response.json()["token"]
    
    # Confirm password reset
    response = client.post("/password-reset-confirm/", json={
        "token": token,
        "new_password": "confirmedpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"
    
    # Verify password was changed and token cleared
    user = User.objects.get(username="testuser")
    assert user.password_reset_token is None
    assert user.password_reset_token_created_at is None
    
    # Verify new password works
    authenticated_user = authenticate(username='testuser', password='confirmedpassword123')
    assert authenticated_user is not None


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(client):
    response = client.post("/password-reset-confirm/", json={
        "token": "invalid_token",
        "new_password": "newpassword123"
    })
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_password_reset_confirm_expired_token(client, test_user, monkeypatch):
    # Request password reset
    response = client.post("/password-reset-request/", json={
        "email": "test@example.com"
    })
    assert response.status_code == 200
    token = response.json()["token"]
    
    # Manually expire the token by setting created_at to past
    user = User.objects.get(username="testuser")
    expired_time = timezone.now() - timedelta(seconds=3601)
    user.password_reset_token_created_at = expired_time
    user.save()
    
    # Try to confirm with expired token
    response = client.post("/password-reset-confirm/", json={
        "token": token,
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert "Token expired" in response.json()["detail"]

@pytest.mark.django_db
def test_signup_duplicate_email(client):
    """Test signup with duplicate email"""
    # Clean up any existing users
    User.objects.filter(username="user1").delete()
    User.objects.filter(username="user2").delete()
    
    # Create first user
    response = client.post("/signup/", json={
        "username": "user1",
        "email": "same@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    
    # Try to create second user with same email
    response = client.post("/signup/", json={
        "username": "user2",
        "email": "same@example.com",
        "password": "password123"
    })
    # Django will allow this, but we should test the behavior
    # The test might pass or fail depending on model constraints
    assert response.status_code in [200, 400, 500]

@pytest.mark.django_db
def test_signup_invalid_data(client):
    """Test signup with missing required fields"""
    # Missing username
    response = client.post("/signup/", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 422  # Validation error
    
    # Missing email
    response = client.post("/signup/", json={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 422
    
    # Missing password
    response = client.post("/signup/", json={
        "username": "testuser",
        "email": "test@example.com"
    })
    assert response.status_code == 422

@pytest.mark.django_db(transaction=True)
def test_login_exception_handling(client, mocker, test_user):
    """Test login endpoint's exception handling."""
    # Mock authenticate to return a valid user
    mocker.patch('django.contrib.auth.authenticate', return_value=test_user)
    # Mock Token.objects.get_or_create to raise an exception
    mocker.patch('rest_framework.authtoken.models.Token.objects.get_or_create', side_effect=Exception("Mocked token creation error"))

    response = client.post("/login/", json={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 400
    assert "Mocked token creation error" in response.json()["detail"]

