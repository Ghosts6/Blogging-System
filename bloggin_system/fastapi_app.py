import os
import django
from django.apps import apps

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bloggin_system.settings")
if not apps.ready:
    django.setup()

from fastapi import FastAPI
from service.api import articles, users, categories, faqs

app = FastAPI()

app.include_router(users.router, tags=["Users"])
app.include_router(articles.router, tags=["Articles"])
app.include_router(categories.router, tags=["Categories"])
app.include_router(faqs.router, tags=["FAQs"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/diagnostics")
def diagnostics():
    import sys
    from service.models import Article, CustomUser, Comment
    return {
        "django_version": django.get_version(),
        "python_version": sys.version,
        "article_count": Article.objects.count(),
        "user_count": CustomUser.objects.count(),
        "comment_count": Comment.objects.count(),
    }
