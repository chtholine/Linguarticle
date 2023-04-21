from django.db import models


class Article(models.Model):
    url = models.URLField(unique=True)
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    data = models.TextField()

    def __str__(self):
        return self.title
