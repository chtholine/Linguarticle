from django.contrib import admin
from .models import *


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "data", "url")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Dictionary)
