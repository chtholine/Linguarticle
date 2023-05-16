from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(required=False, default="Unknown")

    class Meta:
        model = Article
        fields = ["title", "author", "data", "translation"]


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title"]


class DictionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dictionary
        fields = ["word", "translation"]


class UserSerializer(serializers.ModelSerializer):
    errors = serializers.SerializerMethodField()

    def get_errors(self, obj):
        return self.errors if self.errors else {}

    class Meta:
        model = User
        fields = ("username", "email", "password", "errors")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "username": {"required": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        if password := validated_data.get("password"):
            instance.set_password(password)
        instance.save()
        return instance
