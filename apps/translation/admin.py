from django.contrib import admin

from .models import *


class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "id")


admin.site.register(Article, ArticleAdmin)
admin.site.register(Dictionary)
