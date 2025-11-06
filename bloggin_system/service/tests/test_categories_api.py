import pytest

@pytest.mark.django_db
def test_create_category(client):
    # Create a category (no auth required)
    response = client.post("/categories/", json={"name": "New Category"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Category"

@pytest.mark.django_db
def test_list_categories(client):
    # Clean up any existing categories from previous runs
    from service.models import Category
    Category.objects.filter(name__in=["Category 1", "Category 2"]).delete()
    
    # Create some categories via API
    response = client.post("/categories/", json={"name": "Category 1"})
    assert response.status_code == 200
    response = client.post("/categories/", json={"name": "Category 2"})
    assert response.status_code == 200

    # List the categories
    response = client.get("/categories/")
    assert response.status_code == 200
    categories = response.json()
    category_names = [cat["name"] for cat in categories]
    assert "Category 1" in category_names
    assert "Category 2" in category_names

@pytest.mark.django_db
def test_update_category(client):
    # Create a category
    response = client.post("/categories/", json={"name": "Category to update"})
    assert response.status_code == 200
    category_id = response.json()["id"]

    # Update the category
    response = client.put(f"/categories/{category_id}/", json={"name": "Updated category"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated category"

@pytest.mark.django_db
def test_delete_category(client):
    # Clean up any existing category with this name
    from service.models import Category
    Category.objects.filter(name="Category to delete").delete()
    
    # Create a category
    response = client.post("/categories/", json={"name": "Category to delete"})
    assert response.status_code == 200
    category_id = response.json()["id"]

    # Delete the category
    response = client.delete(f"/categories/{category_id}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"

    # Verify that the category is deleted
    response = client.get("/categories/")
    assert response.status_code == 200
    categories = response.json()
    category_names = [cat["name"] for cat in categories]
    assert "Category to delete" not in category_names

@pytest.mark.django_db
def test_delete_category_not_found(client):
    """Test deleting non-existent category"""
    response = client.delete("/categories/999/")
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]

@pytest.mark.django_db
def test_update_category_not_found(client):
    """Test updating non-existent category"""
    response = client.put("/categories/999/", json={"name": "Updated name"})
    assert response.status_code == 404
    assert "Category not found" in response.json()["detail"]

@pytest.mark.django_db
def test_create_category_invalid_data(client):
    """Test creating category with missing name"""
    response = client.post("/categories/", json={})
    assert response.status_code == 422

@pytest.mark.django_db
def test_update_category_invalid_data(client):
    """Test updating category with missing name"""
    # Create category first
    response = client.post("/categories/", json={"name": "Test Category"})
    assert response.status_code == 200
    category_id = response.json()["id"]
    
    # Try to update without name
    response = client.put(f"/categories/{category_id}/", json={})
    assert response.status_code == 422
