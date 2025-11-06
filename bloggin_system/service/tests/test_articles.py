import pytest
from service.models import Article, Category
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db(transaction=True)
def test_list_articles(client, test_user):
    # Log in and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create articles using the API
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/articles/", headers=headers, json={"title": "Test Article 1", "content": "Test Content 1", "tags": "test"})
    client.post("/articles/", headers=headers, json={"title": "Test Article 2", "content": "Test Content 2", "tags": "test"})

    # List the articles
    response = client.get("/articles/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Test Article 1"
    assert response.json()[1]["title"] == "Test Article 2"

@pytest.mark.django_db(transaction=True)
def test_list_articles_filtering(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create some articles with different authors, categories, and tags
    user2 = User.objects.create_user(username="testuser2", password="testpassword")

    # Article 1
    client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article 1", "content": "Content 1", "tags": "tag1,tag2"})
    # Article 2
    client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article 2", "content": "Content 2", "tags": "tag2,tag3"})
    # Article 3 (by user2)
    # To create an article by user2, we need to log in as user2 and get a token
    response = client.post("/login/", json={"username": "testuser2", "password": "testpassword"})
    assert response.status_code == 200
    token2 = response.json()["access_token"]
    client.post("/articles/", headers={"Authorization": f"Bearer {token2}"}, json={"title": "Article 3", "content": "Content 3", "tags": "tag3,tag4"})

    # Test filtering by author
    response = client.get("/articles/?author=testuser")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Article 1"
    assert response.json()[1]["title"] == "Article 2"

    response = client.get("/articles/?author=testuser2")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Article 3"

    # Test filtering by tags
    response = client.get("/articles/?tags=tag1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Article 1"

    response = client.get("/articles/?tags=tag2")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Article 1"
    assert response.json()[1]["title"] == "Article 2"

    # Test filtering by search
    response = client.get("/articles/?search=Content 1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Article 1"

    response = client.get("/articles/?search=Content")
    assert response.status_code == 200
    assert len(response.json()) == 3

@pytest.mark.django_db(transaction=True)
def test_update_article(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an article
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article to update", "content": "Content to update", "tags": "tags_to_update"})
    assert response.status_code == 200
    article_id = response.json()["id"]

    # Update the article
    response = client.put(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Updated title", "content": "Updated content", "tags": "updated_tags"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"
    assert response.json()["content"] == "Updated content"
    assert response.json()["tags"] == "updated_tags"

@pytest.mark.django_db(transaction=True)
def test_delete_article(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an article
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article to delete", "content": "Content to delete", "tags": "tags_to_delete"})
    assert response.status_code == 200
    article_id = response.json()["id"]

    # Delete the article
    response = client.delete(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Article deleted successfully"

    # Verify that the article is deleted
    response = client.get(f"/articles/{article_id}/")
    assert response.status_code == 404

@pytest.mark.django_db(transaction=True)
def test_create_comment(client, test_user, mocker):
    # Mock the Celery task
    mock_send_email = mocker.patch('service.api.articles.send_comment_notification_email.delay')

    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an article
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article for comment", "content": "Content for comment", "tags": "tags_for_comment"})
    assert response.status_code == 200
    article_id = response.json()["id"]

    # Create a comment
    response = client.post(f"/articles/{article_id}/comments/", headers={"Authorization": f"Bearer {token}"}, json={"content": "This is a comment"})
    assert response.status_code == 200
    assert response.json()["content"] == "This is a comment"
    assert response.json()["user"]["username"] == "testuser"
    mock_send_email.assert_called_once_with(mocker.ANY, mocker.ANY)

@pytest.mark.django_db(transaction=True)
def test_list_comments(client, test_user):
    # Log in as test_user and get the token
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Create an article
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article for comments", "content": "Content for comments", "tags": "tags_for_comments"})
    assert response.status_code == 200
    article_id = response.json()["id"]

    # Create some comments
    client.post(f"/articles/{article_id}/comments/", headers={"Authorization": f"Bearer {token}"}, json={"content": "Comment 1"})
    client.post(f"/articles/{article_id}/comments/", headers={"Authorization": f"Bearer {token}"}, json={"content": "Comment 2"})

    # List the comments
    response = client.get(f"/articles/{article_id}/comments/")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["content"] == "Comment 1"
    assert response.json()[1]["content"] == "Comment 2"

@pytest.mark.django_db(transaction=True)
def test_create_article_unauthorized(client):
    """Test creating article without authentication"""
    response = client.post("/articles/", json={"title": "Test", "content": "Test", "tags": "test"})
    assert response.status_code in [401, 403, 422]

@pytest.mark.django_db(transaction=True)
def test_get_article_not_found(client):
    """Test getting non-existent article"""
    response = client.get("/articles/999/")
    assert response.status_code == 404
    assert "Article not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_update_article_not_found(client, test_user):
    """Test updating non-existent article"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.put("/articles/999/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test", "content": "Test", "tags": "test"})
    assert response.status_code == 404
    assert "Article not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_update_article_unauthorized(client, test_user):
    """Test updating another user's article"""
    # Create user2
    User.objects.filter(username="testuser2").delete()
    user2 = User.objects.create_user(username="testuser2", password="testpassword2", email="user2@example.com")
    
    # Login as user2 and create article
    response = client.post("/login/", json={"username": "testuser2", "password": "testpassword2"})
    assert response.status_code == 200
    token2 = response.json()["access_token"]
    
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token2}"}, json={"title": "User2 Article", "content": "Content", "tags": "test"})
    assert response.status_code == 200
    article_id = response.json()["id"]
    
    # Try to update as testuser (different user)
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.put(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Hacked", "content": "Hacked", "tags": "test"})
    assert response.status_code == 404  # Article not found because it belongs to user2

@pytest.mark.django_db(transaction=True)
def test_delete_article_not_found(client, test_user):
    """Test deleting non-existent article"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.delete("/articles/999/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Article not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_delete_article_unauthorized(client, test_user):
    """Test deleting another user's article"""
    # Create user2
    User.objects.filter(username="testuser2").delete()
    user2 = User.objects.create_user(username="testuser2", password="testpassword2", email="user2@example.com")
    
    # Login as user2 and create article
    response = client.post("/login/", json={"username": "testuser2", "password": "testpassword2"})
    assert response.status_code == 200
    token2 = response.json()["access_token"]
    
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token2}"}, json={"title": "User2 Article", "content": "Content", "tags": "test"})
    assert response.status_code == 200
    article_id = response.json()["id"]
    
    # Try to delete as testuser (different user)
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.delete(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404  # Article not found because it belongs to user2

@pytest.mark.django_db(transaction=True)
def test_create_comment_unauthorized(client, test_user):
    """Test creating comment without authentication"""
    # Create article first
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test", "content": "Test", "tags": "test"})
    assert response.status_code == 200
    article_id = response.json()["id"]
    
    # Try to comment without auth
    response = client.post(f"/articles/{article_id}/comments/", json={"content": "Test comment"})
    assert response.status_code in [401, 403, 422]

@pytest.mark.django_db(transaction=True)
def test_create_comment_article_not_found(client, test_user):
    """Test creating comment on non-existent article"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    response = client.post("/articles/999/comments/", headers={"Authorization": f"Bearer {token}"}, json={"content": "Test comment"})
    assert response.status_code == 404
    assert "Article not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_list_comments_article_not_found(client):
    """Test listing comments for non-existent article"""
    response = client.get("/articles/999/comments/")
    assert response.status_code == 404
    assert "Article not found" in response.json()["detail"]

@pytest.mark.django_db(transaction=True)
def test_list_articles_pagination(client, test_user):
    """Test article list pagination"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Create 15 articles
    for i in range(15):
        client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": f"Article {i}", "content": f"Content {i}", "tags": "test"})
    
    # Test default pagination (limit=10)
    response = client.get("/articles/")
    assert response.status_code == 200
    assert len(response.json()) == 10
    
    # Test custom pagination
    response = client.get("/articles/?skip=5&limit=5")
    assert response.status_code == 200
    assert len(response.json()) == 5

@pytest.mark.django_db(transaction=True)
def test_create_article_invalid_data(client, test_user):
    """Test creating article with missing required fields"""
    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Missing title
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"content": "Content only", "tags": "test"})
    assert response.status_code == 422
    
    # Missing content
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Title only", "tags": "test"})
    assert response.status_code == 422
    
    # Missing tags
    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Title", "content": "Content"})
    # Tags might be optional, so this might pass
    assert response.status_code in [200, 422]

@pytest.mark.django_db(transaction=True)

def test_delete_article_with_invalid_token(client, test_user):

    """Test deleting an article with an invalid token."""

    # Log in as test_user and get the token

    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200

    token = response.json()["access_token"]



    # Create an article

    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article to delete", "content": "Content to delete", "tags": "tags_to_delete"})

    assert response.status_code == 200

    article_id = response.json()["id"]



    # Try to delete with an invalid token

    headers = {"Authorization": f"Bearer invalid_token"}

    response = client.delete(f"/articles/{article_id}/", headers=headers)

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid token"



@pytest.mark.django_db(transaction=True)

def test_update_article_with_invalid_token(client, test_user):

    """Test updating an article with an invalid token."""

    # Log in as test_user and get the token

    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200

    token = response.json()["access_token"]



    # Create an article

    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Article to update", "content": "Content to update", "tags": "tags_to_update"})

    assert response.status_code == 200

    article_id = response.json()["id"]



    # Try to update with an invalid token

    headers = {"Authorization": f"Bearer invalid_token"}

    response = client.put(f"/articles/{article_id}/", headers=headers, json={"title": "Updated title", "content": "Updated content", "tags": "updated_tags"})

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid token"



@pytest.mark.django_db(transaction=True)

def test_create_article_with_invalid_token(client):

    """Test creating an article with an invalid token."""

    headers = {"Authorization": f"Bearer invalid_token"}

    response = client.post("/articles/", headers=headers, json={"title": "Test Article", "content": "Test Content", "tags": "test"})

    assert response.status_code == 401

    assert response.json()["detail"] == "Invalid token"



@pytest.mark.django_db(transaction=True)

def test_list_articles_filter_by_category(client, test_user):

    # Log in as test_user and get the token

    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200

    token = response.json()["access_token"]



    # Create a category

    category = Category.objects.create(name="TestCategory")



    # Create an article and associate it with the category

    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Categorized Article", "content": "Content for category", "tags": "category_tag"})

    assert response.status_code == 200

    article_id = response.json()["id"]

    article = Article.objects.get(id=article_id)

    article.categories.add(category)

    article.save()



    # Create another article not in the category

    client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Uncategorized Article", "content": "Content for uncategorized", "tags": "uncategorized_tag"})



    # Test filtering by category

    response = client.get(f"/articles/?category={category.name}")

    assert response.status_code == 200

    assert len(response.json()) == 1

    assert response.json()[0]["title"] == "Categorized Article"



@pytest.mark.django_db(transaction=True)

def test_update_article_invalid_data(client, test_user):

    """Test updating article with missing required fields"""

    response = client.post("/login/", json={"username": "testuser", "password": "testpassword"})

    assert response.status_code == 200

    token = response.json()["access_token"]

    

    # Create article first

    response = client.post("/articles/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Test", "content": "Test", "tags": "test"})

    assert response.status_code == 200

    article_id = response.json()["id"]

    

    # Missing title

    response = client.put(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"}, json={"content": "Content only", "tags": "test"})

    assert response.status_code == 422

    

    # Missing content

    response = client.put(f"/articles/{article_id}/", headers={"Authorization": f"Bearer {token}"}, json={"title": "Title only", "tags": "test"})

    assert response.status_code == 422



@pytest.mark.django_db(transaction=True)

def test_diagnostics_endpoint(client):

    """Test the /diagnostics endpoint."""

    response = client.get("/diagnostics")

    assert response.status_code == 200

    data = response.json()

    assert "django_version" in data

    assert "python_version" in data

    assert "article_count" in data

    assert "user_count" in data

    assert "comment_count" in data

    assert isinstance(data["article_count"], int)

    assert isinstance(data["user_count"], int)

    assert isinstance(data["comment_count"], int)


