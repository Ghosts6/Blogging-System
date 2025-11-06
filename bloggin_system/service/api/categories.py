from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from service.schemas import CategorySerializer
from service.models import Category

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str

@router.post("/categories/", response_model=CategorySerializer)
def create_category(category: CategoryCreate):
    new_category = Category.objects.create(name=category.name)
    return CategorySerializer.model_validate(new_category)

@router.get("/categories/", response_model=List[CategorySerializer])
def list_categories():
    categories = Category.objects.all()
    return [CategorySerializer.model_validate(category) for category in categories]

@router.put("/categories/{category_id}/", response_model=CategorySerializer)
def update_category(category_id: int, category: CategoryCreate):
    try:
        existing_category = Category.objects.get(id=category_id)
        existing_category.name = category.name
        existing_category.save()
        return CategorySerializer.model_validate(existing_category)
    except Category.DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")

@router.delete("/categories/{category_id}/", response_model=dict)
def delete_category(category_id: int):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return {"message": "Category deleted successfully"}
    except Category.DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
