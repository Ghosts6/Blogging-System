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
from service.schemas import ArticleSerializer, UserSerializer, FAQSerializer, CategorySerializer ,CommentSerializer
from service.models import Article, FAQ, Category, Comment
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
    
class FAQCreate(BaseModel):
    question: str
    answer: str

class CategoryCreate(BaseModel):
    name: str

class CommentCreate(BaseModel):
    content: str

#   Authentication api

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

#   Articles api

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

@app.post("/categories/", response_model=CategorySerializer)
def create_category(category: CategoryCreate):
    new_category = Category.objects.create(name=category.name)
    return CategorySerializer.from_orm(new_category)

@app.get("/categories/", response_model=List[CategorySerializer])
def list_categories():
    categories = Category.objects.all()
    return [CategorySerializer.from_orm(category) for category in categories]

@app.post("/articles/{article_id}/comments/", response_model=CommentSerializer)
def create_comment(article_id: int, comment: CommentCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        article = Article.objects.get(id=article_id)
        new_comment = Comment.objects.create(article=article, user=user, content=comment.content)
        return CommentSerializer.from_orm(new_comment)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@app.get("/articles/{article_id}/comments/", response_model=List[CommentSerializer])
def list_comments(article_id: int):
    article = Article.objects.get(id=article_id)
    comments = article.comments.all()
    return [CommentSerializer.from_orm(comment) for comment in comments]

#   Faqs api

@app.post("/faqs/", response_model=FAQSerializer)
def create_faq(faq: FAQCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        new_faq = FAQ.objects.create(question=faq.question, answer=faq.answer, created_by=user)
        return FAQSerializer.from_orm(new_faq)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/faqs/", response_model=List[FAQSerializer])
def list_faqs():
    faqs = FAQ.objects.all()
    return [FAQSerializer.from_orm(faq) for faq in faqs]

@app.get("/faqs/{faq_id}/", response_model=FAQSerializer)
def get_faq(faq_id: int):
    try:
        faq = FAQ.objects.get(id=faq_id)
        return FAQSerializer.from_orm(faq)
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")

@app.put("/faqs/{faq_id}/", response_model=FAQSerializer)
def update_faq(faq_id: int, faq: FAQCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        existing_faq = FAQ.objects.get(id=faq_id, created_by=user)
        existing_faq.question = faq.question
        existing_faq.answer = faq.answer
        existing_faq.save()
        return FAQSerializer.from_orm(existing_faq)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")

@app.delete("/faqs/{faq_id}/")
def delete_faq(faq_id: int, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        faq = FAQ.objects.get(id=faq_id, created_by=user)
        faq.delete()
        return {"message": "FAQ deleted successfully"}
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except FAQ.DoesNotExist:
        raise HTTPException(status_code=404, detail="FAQ not found")