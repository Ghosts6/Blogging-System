from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserSerializer(BaseModel):
    id: int
    username: str
    email: str

class ArticleSerializer(BaseModel):
    id: int
    title: str
    content: str
    author: UserSerializer
    published_date: datetime
    tags: Optional[str] = None

    model_config = {"from_attributes": True}
        
class FAQSerializer(BaseModel):
    id: int
    question: str
    answer: str
    created_by: UserSerializer

    model_config = {"from_attributes": True}

class CategorySerializer(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class CommentSerializer(BaseModel):
    id: int
    article_id: int
    user: UserSerializer
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}