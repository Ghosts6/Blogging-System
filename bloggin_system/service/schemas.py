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