import pytest
from django.db import transaction


@pytest.mark.django_db(transaction=True)
def test_create_faq(client, test_user):
    # Log in and get token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create FAQ
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "What is this?", "answer": "This is a test FAQ"}
    )
    assert response.status_code == 200
    assert response.json()["question"] == "What is this?"
    assert response.json()["answer"] == "This is a test FAQ"


@pytest.mark.django_db
def test_create_faq_unauthorized(client):
    # Try to create FAQ without token
    response = client.post(
        "/faqs/",
        json={"question": "What is this?", "answer": "This is a test FAQ"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.django_db(transaction=True)
def test_list_faqs(client, test_user):
    from service.models import FAQ
    # Create some FAQs directly in the database
    FAQ.objects.create(question="Question 1", answer="Answer 1", created_by=test_user)
    FAQ.objects.create(question="Question 2", answer="Answer 2", created_by=test_user)
    
    # List FAQs (no auth required for listing)
    response = client.get("/faqs/")
    assert response.status_code == 200
    faqs = response.json()
    assert len(faqs) == 2
    questions = [faq["question"] for faq in faqs]
    assert "Question 1" in questions
    assert "Question 2" in questions


@pytest.mark.django_db(transaction=True)
def test_get_faq(client, test_user):
    # Log in and get token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create FAQ
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Test Question", "answer": "Test Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Get FAQ
    response = client.get(f"/faqs/{faq_id}/")
    assert response.status_code == 200
    assert response.json()["question"] == "Test Question"
    assert response.json()["answer"] == "Test Answer"


@pytest.mark.django_db
def test_get_faq_not_found(client):
    response = client.get("/faqs/999/")
    assert response.status_code == 404
    assert "FAQ not found" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_update_faq(client, test_user):
    # Log in and get token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create FAQ
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Original Question", "answer": "Original Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Update FAQ
    response = client.put(
        f"/faqs/{faq_id}/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Updated Question", "answer": "Updated Answer"}
    )
    assert response.status_code == 200
    assert response.json()["question"] == "Updated Question"
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"


@pytest.mark.django_db(transaction=True)
def test_update_faq_not_found(client, test_user):
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.put(
        "/faqs/999/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Updated Question", "answer": "Updated Answer"}
    )
    assert response.status_code == 404
    assert "FAQ not found" in response.json()["detail"]


@pytest.mark.django_db(transaction=True)
def test_delete_faq(client, test_user):
    # Log in and get token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create FAQ
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Question to delete", "answer": "Answer to delete"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Delete FAQ
    response = client.delete(
        f"/faqs/{faq_id}/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "FAQ deleted successfully"
    
    # Verify FAQ is deleted
    response = client.get(f"/faqs/{faq_id}/")
    assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
def test_delete_faq_unauthorized(client, test_user):
    # Log in and create FAQ
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Test Question", "answer": "Test Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Try to delete without token
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.django_db(transaction=True)
def test_delete_faq_unauthorized(client, test_user):
    # Log in and create FAQ
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Test Question", "answer": "Test Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Try to delete with invalid token
    response = client.delete(f"/faqs/{faq_id}/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.django_db(transaction=True)
def test_update_faq_unauthorized(client, test_user):
    # Log in and create FAQ
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Test Question", "answer": "Test Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Try to update with an invalid token
    response = client.put(
        f"/faqs/{faq_id}/",
        headers={"Authorization": "Bearer invalid_token"},
        json={"question": "Updated Question", "answer": "Updated Answer"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.django_db(transaction=True)
def test_create_faq_unauthorized(client):
    """Test creating an FAQ without authentication."""
    response = client.post("/faqs/", json={
        "question": "Unauthorized Question",
        "answer": "Unauthorized Answer"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.django_db(transaction=True)
def test_delete_faq_not_found(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Try to delete a non-existent FAQ
    response = client.delete("/faqs/999/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "FAQ not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_update_faq_not_found(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Try to update a non-existent FAQ
    response = client.put("/faqs/999/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Updated Question",
        "answer": "Updated Answer"
    })
    assert response.status_code == 404
    assert "FAQ not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_list_faqs(client, test_user):
    # Log in and get token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create some FAQs
    client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Question 1", "answer": "Answer 1"}
    )
    client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Question 2", "answer": "Answer 2"}
    )

    # List the FAQs
    response = client.get("/faqs/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["question"] == "Question 1"
    assert response.json()[1]["question"] == "Question 2"

@pytest.mark.django_db(transaction=True)
def test_create_faq(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an FAQ
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Test Question",
        "answer": "Test Answer"
    })
    assert response.status_code == 200
    assert response.json()["question"] == "Test Question"
    assert response.json()["answer"] == "Test Answer"

@pytest.mark.django_db(transaction=True)
def test_get_faq(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an FAQ
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Test Question",
        "answer": "Test Answer"
    })
    assert response.status_code == 200
    faq_id = response.json()["id"]

    # Get the FAQ
    response = client.get(f"/faqs/{faq_id}/")
    assert response.status_code == 200
    assert response.json()["question"] == "Test Question"
    assert response.json()["answer"] == "Test Answer"

@pytest.mark.django_db(transaction=True)
def test_update_faq(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an FAQ
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Question to update",
        "answer": "Answer to update"
    })
    assert response.status_code == 200
    faq_id = response.json()["id"]

    # Update the FAQ
    response = client.put(f"/faqs/{faq_id}/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Updated Question",
        "answer": "Updated Answer"
    })
    assert response.status_code == 200
    assert response.json()["question"] == "Updated Question"
    assert response.json()["answer"] == "Updated Answer"

@pytest.mark.django_db(transaction=True)
def test_delete_faq(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an FAQ
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Question to delete",
        "answer": "Answer to delete"
    })
    assert response.status_code == 200
    faq_id = response.json()["id"]

    # Delete the FAQ
    response = client.delete(f"/faqs/{faq_id}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "FAQ deleted successfully"

    # Verify that the FAQ is deleted
    response = client.get(f"/faqs/{faq_id}/")
    assert response.status_code == 404

@pytest.mark.django_db(transaction=True)
def test_create_faq_invalid_data(client, test_user):
    """Test creating FAQ with missing required fields"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Missing question
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "answer": "Answer only"
    })
    assert response.status_code == 422
    
    # Missing answer
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={
        "question": "Question only"
    })
    assert response.status_code == 422

@pytest.mark.django_db(transaction=True)
def test_update_faq_invalid_token(client, test_user):
    # Log in and create FAQ
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post(
        "/faqs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Test Question", "answer": "Test Answer"}
    )
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Try to update with invalid token
    response = client.put(
        f"/faqs/{faq_id}/",
        headers={"Authorization": "Bearer invalid_token"},
        json={"question": "Updated Question", "answer": "Updated Answer"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

@pytest.mark.django_db(transaction=True)
def test_create_faq_invalid_data(client, test_user):
    """Test creating FAQ with missing required fields"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Missing question
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={"answer": "Answer only"})
    assert response.status_code == 422
    
    # Missing answer
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={"question": "Question only"})
    assert response.status_code == 422

@pytest.mark.django_db(transaction=True)
def test_update_faq_invalid_data(client, test_user):
    """Test updating FAQ with missing required fields"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create FAQ first
    response = client.post("/faqs/", headers={"Authorization": f"Bearer {token}"}, json={"question": "Test", "answer": "Test"})
    assert response.status_code == 200
    faq_id = response.json()["id"]
    
    # Missing question
    response = client.put(f"/faqs/{faq_id}/", headers={"Authorization": f"Bearer {token}"}, json={"answer": "Answer only"})
    assert response.status_code == 422
    
    # Missing answer
    response = client.put(f"/faqs/{faq_id}/", headers={"Authorization": f"Bearer {token}"}, json={"question": "Question only"})
    assert response.status_code == 422