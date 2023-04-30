from django.contrib.auth.models import AbstractUser, User
from django.db import models


class Dictionary(models.Model):
    user = models.ManyToManyField(User, related_name="words")
    word = models.CharField(max_length=255)
    translation = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Dictionary"

    def __str__(self):
        return self.word


class Article(models.Model):
    user = models.ManyToManyField(User, related_name="articles")
    url = models.URLField(unique=True)
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    data = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
