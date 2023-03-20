from abc import ABC

from .models import *
from rest_framework import serializers


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(required=False, default="Unknown")

    class Meta:
        model = Article
        fields = "__all__"
