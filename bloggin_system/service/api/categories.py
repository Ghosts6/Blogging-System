from fastapi import APIRouter
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
    return CategorySerializer.from_orm(new_category)

@router.get("/categories/", response_model=List[CategorySerializer])
def list_categories():
    categories = Category.objects.all()
    return [CategorySerializer.from_orm(category) for category in categories]
