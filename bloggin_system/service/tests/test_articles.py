import pytest
from service.models import Article

# @pytest.mark.django_db
# def test_list_articles(client, test_user):
#     # Log in and get the token
#     response = client.post("/login/", data={"username": "testuser", "password": "testpassword"})
#     assert response.status_code == 200
#     token = response.json()["access_token"]

#     # Create articles using the API
#     headers = {"Authorization": f"Bearer {token}"}
#     client.post("/articles/", headers=headers, json={"title": "Test Article 1", "content": "Test Content 1", "tags": "test"})
#     client.post("/articles/", headers=headers, json={"title": "Test Article 2", "content": "Test Content 2", "tags": "test"})

#     # List the articles
#     response = client.get("/articles/")

#     assert response.status_code == 200
#     assert len(response.json()) == 2
#     assert response.json()[0]["title"] == "Test Article 1"
#     assert response.json()[1]["title"] == "Test Article 2"
