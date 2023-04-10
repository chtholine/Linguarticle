from django.db import models


class Article(models.Model):
    url = models.URLField(max_length=255)
    author = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    data = models.TextField()

    def __str__(self):
        return self.title
