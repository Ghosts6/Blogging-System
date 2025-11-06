from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from service.schemas import ArticleSerializer, CommentSerializer, UserSerializer
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
    result = []
    for article in articles:
        result.append(ArticleSerializer(
            id=article.id,
            title=article.title,
            content=article.content,
            author=UserSerializer(
                id=article.author.id,
                username=article.author.username,
                email=article.author.email
            ),
            published_date=article.published_date,
            tags=article.tags
        ))
    return result

@router.post("/articles/", response_model=ArticleSerializer)
def create_article(article: ArticleCreate, token: str = Depends(oauth2_scheme)):
    try:
        user = Token.objects.get(key=token).user
        new_article = Article.objects.create(title=article.title, content=article.content, tags=article.tags, author=user)
        # Manually construct serializer to handle author relationship
        return ArticleSerializer(
            id=new_article.id,
            title=new_article.title,
            content=new_article.content,
            author=UserSerializer(
                id=user.id,
                username=user.username,
                email=user.email
            ),
            published_date=new_article.published_date,
            tags=new_article.tags
        )
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/articles/{article_id}/", response_model=ArticleSerializer)
def get_article(article_id: int):
    try:
        article = Article.objects.get(id=article_id)
        # Manually construct serializer to handle author relationship
        return ArticleSerializer(
            id=article.id,
            title=article.title,
            content=article.content,
            author=UserSerializer(
                id=article.author.id,
                username=article.author.username,
                email=article.author.email
            ),
            published_date=article.published_date,
            tags=article.tags
        )
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
        # Manually construct serializer to handle author relationship
        return ArticleSerializer(
            id=existing_article.id,
            title=existing_article.title,
            content=existing_article.content,
            author=UserSerializer(
                id=user.id,
                username=user.username,
                email=user.email
            ),
            published_date=existing_article.published_date,
            tags=existing_article.tags
        )
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
        # Manually construct serializer to handle user relationship
        return CommentSerializer(
            id=new_comment.id,
            article_id=article.id,
            user=UserSerializer(
                id=user.id,
                username=user.username,
                email=user.email
            ),
            content=new_comment.content,
            created_at=new_comment.created_at
        )
    except Token.DoesNotExist:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")

@router.get("/articles/{article_id}/comments/", response_model=List[CommentSerializer])
def list_comments(article_id: int):
    try:
        article = Article.objects.get(id=article_id)
        comments = article.comments.all()
        result = []
        for comment in comments:
            result.append(CommentSerializer(
                id=comment.id,
                article_id=article.id,
                user=UserSerializer(
                    id=comment.user.id,
                    username=comment.user.username,
                    email=comment.user.email
                ),
                content=comment.content,
                created_at=comment.created_at
            ))
        return result
    except Article.DoesNotExist:
        raise HTTPException(status_code=404, detail="Article not found")
