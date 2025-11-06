from pydantic import BaseModel, field_serializer, model_validator
from typing import List, Optional, Union
from datetime import datetime
from service.models import CustomUser

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

    @field_serializer('author')
    def serialize_author(self, author: Union[dict, CustomUser], _info):
        if isinstance(author, CustomUser):
            return UserSerializer(id=author.id, username=author.username, email=author.email)
        return author

class FAQSerializer(BaseModel):
    id: int
    question: str
    answer: str
    created_by: UserSerializer

    model_config = {"from_attributes": True}

    @field_serializer('created_by')
    def serialize_created_by(self, created_by: CustomUser, _info):
        return UserSerializer(id=created_by.id, username=created_by.username, email=created_by.email)

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

    @field_serializer('user')
    def serialize_user(self, user: CustomUser, _info):
        return UserSerializer(id=user.id, username=user.username, email=user.email)