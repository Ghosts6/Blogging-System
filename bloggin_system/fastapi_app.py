import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bloggin_system.settings")
django.setup()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from service.schemas import ArticleSerializer, UserSerializer  
from service.models import Article 
from rest_framework.authtoken.models import Token
from django.conf import settings

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: str

@app.post("/signup/")
def create_user(user: UserCreate):
    if User.objects.filter(username=user.username).exists():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User.objects.create_user(username=user.username, email=user.email, password=user.password)
    return {"message": "User created successfully"}

@app.post("/login/")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate(username=form_data.username, password=form_data.password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return {"access_token": token.key, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/password_reset/")
def reset_password(username: str, new_password: str):
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        return {"message": "Password updated successfully"}
    except ObjectDoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")

@app.get("/articles/", response_model=List[ArticleSerializer])
def list_articles():
    articles = Article.objects.all()
    return [ArticleSerializer.from_orm(article) for article in articles]

@app.post("/articles/", response_model=ArticleSerializer)
def create_article(article: ArticleCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        new_article = Article.objects.create(title=article.title, content=article.content, tags=article.tags, author=user)
        return ArticleSerializer.from_orm(new_article)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/articles/{article_id}/", response_model=ArticleSerializer)
def get_article(article_id: int):
    try:
        article = Article.objects.get(id=article_id)
        return ArticleSerializer.from_orm(article)
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@app.put("/articles/{article_id}/", response_model=ArticleSerializer)
def update_article(article_id: int, article: ArticleCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        existing_article = Article.objects.get(id=article_id, author=user)
        existing_article.title = article.title
        existing_article.content = article.content
        existing_article.tags = article.tags
        existing_article.save()
        return ArticleSerializer(existing_article).data
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@app.delete("/articles/{article_id}/")
def delete_article(article_id: int, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        article = Article.objects.get(id=article_id, author=user)
        article.delete()
        return {"message": "Article deleted successfully"}
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")
