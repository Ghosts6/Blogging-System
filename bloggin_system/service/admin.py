from django.contrib import admin
from .models import Article, CustomUser, FAQ

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff')

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_date', 'tags')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('author', 'published_date', 'tags')

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'created_at')
    search_fields = ('question',)
    list_filter = ('created_by',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(FAQ, FAQAdmin)