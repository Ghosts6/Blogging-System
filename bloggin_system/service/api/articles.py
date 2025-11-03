from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from service.schemas import ArticleSerializer, CommentSerializer
from service.models import Article, Comment
from rest_framework.authtoken.models import Token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: str

class CommentCreate(BaseModel):
    content: str

from django.db.models import Q

@router.get("/articles/", response_model=List[ArticleSerializer])
def list_articles(author: str = None, category: str = None, tags: str = None, search: str = None, skip: int = 0, limit: int = 10):
    articles = Article.objects.all()
    if author:
        articles = articles.filter(author__username=author)
    if category:
        articles = articles.filter(categories__name=category)
    if tags:
        articles = articles.filter(tags__icontains=tags)
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(content__icontains=search))
    articles = articles[skip : skip + limit]
    return [ArticleSerializer.from_orm(article) for article in articles]

@router.post("/articles/", response_model=ArticleSerializer)
def create_article(article: ArticleCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        new_article = Article.objects.create(title=article.title, content=article.content, tags=article.tags, author=user)
        return ArticleSerializer.from_orm(new_article)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/articles/{article_id}/", response_model=ArticleSerializer)
def get_article(article_id: int):
    try:
        article = Article.objects.get(id=article_id)
        return ArticleSerializer.from_orm(article)
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@router.put("/articles/{article_id}/", response_model=ArticleSerializer)
def update_article(article_id: int, article: ArticleCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        existing_article = Article.objects.get(id=article_id, author=user)
        existing_article.title = article.title
        existing_article.content = article.content
        existing_article.tags = article.tags
        existing_article.save()
        return ArticleSerializer.from_orm(existing_article)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@router.delete("/articles/{article_id}/")
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

from service.tasks import send_comment_notification_email

@router.post("/articles/{article_id}/comments/", response_model=CommentSerializer)
def create_comment(article_id: int, comment: CommentCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        article = Article.objects.get(id=article_id)
        new_comment = Comment.objects.create(article=article, user=user, content=comment.content)
        send_comment_notification_email.delay(article.author.email, article.title)
        return CommentSerializer.from_orm(new_comment)
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@router.get("/articles/{article_id}/comments/", response_model=List[CommentSerializer])
def list_comments(article_id: int):
    try:
        article = Article.objects.get(id=article_id)
        comments = article.comments.all()
        return [CommentSerializer.from_orm(comment) for comment in comments]
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")
