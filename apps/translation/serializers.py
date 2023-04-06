from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.CharField(required=False, default="Unknown")

    class Meta:
        model = Article
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    errors = serializers.SerializerMethodField()

    def get_errors(self, obj):
        if self.errors:
            return self.errors
        return {}

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        instance.save()
        return instance
