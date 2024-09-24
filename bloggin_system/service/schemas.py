from pydantic import BaseModel
from typing import List, Optional

class UserSerializer(BaseModel):
    id: int
    username: str
    email: str

class ArticleSerializer(BaseModel):
    id: int
    title: str
    content: str
    author: UserSerializer
    published_date: str
    tags: Optional[str] = None

    class Config:
        orm_mode = True
        
class FAQSerializer(BaseModel):
    id: int
    question: str
    answer: str
    created_by: UserSerializer

    class Config:
        orm_mode = True

class CategorySerializer(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class CommentSerializer(BaseModel):
    id: int
    article_id: int
    user: UserSerializer
    content: str
    created_at: str

    class Config:
        orm_mode = True
