import os
import nltk
from deep_translator import GoogleTranslator
import subprocess
from drf_yasg import openapi
import requests
from bs4 import BeautifulSoup
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer, DictionarySerializer
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Article, Dictionary
from .serializers import ArticleSerializer
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import render


def url_valid(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False
    return True


def submit_url(request):
    return render(request, "add_article.html")


# --- Auth --- #
class SignUpAPIView(APIView):
    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user is not None:
                refresh = RefreshToken.for_user(user)
                response_data = {
                    "status": "success",
                    "message": "User created successfully.",
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["username", "password"],
        )
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response_data = {
                "status": "success",
                "message": "Login successful.",
                "data": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


# --Settings-- #
class UpdateUsernameAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Username updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEmailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=UserSerializer)
    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(type=openapi.TYPE_STRING),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["old_password", "new_password"],
        )
    )
    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid old password."}, status=status.HTTP_400_BAD_REQUEST)


# -- Articles -- #
class ArticlesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        articles = Article.objects.filter(user=request.user).order_by("-date_added")
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class AddArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT, properties={"url": openapi.Schema(type=openapi.TYPE_STRING)}, required=["url"]
        )
    )
    def post(self, request):
        # canonical url check
        url = request.data.get("url")
        if url is None:
            return Response({"error": "URL parameter is missing."}, status=400)
        if not url_valid(url):
            return Response({"error": "URL is invalid."}, status=400)
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        link_tag = soup.find("link", rel="canonical")
        canonical_url = link_tag["href"] if link_tag is not None else url
        if Article.objects.filter(url=canonical_url).exists():
            article = Article.objects.get(url=canonical_url)
            article.user.add(request.user)
            article.save()
            return Response({"error": "Existing article is added to the user."}, status=400)

        # launch scrapy spider with subprocess
        os.environ["PYTHONPATH"] = "/home/chtholine/PycharmProjects/django_translation/scraper"
        spider_name = "article_spider"
        user_id = request.user.id
        command = f"scrapy crawl {spider_name} -a url={canonical_url} -a user_id={user_id}"
        try:
            subprocess.run(
                command.split(), check=True, cwd="/home/chtholine/PycharmProjects/django_translation/scraper"
            )
            return Response({"message": f"{spider_name} spider started for URL: {canonical_url}"})
        except subprocess.CalledProcessError as e:
            return Response({"error": str(e)}, status=500)


class ShowArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        article = Article.objects.get(id=id, user=request.user)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)


class UpdateArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=ArticleSerializer)
    def put(self, request, id):
        article = Article.objects.get(id=id, user=request.user)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        article = Article.objects.get(id=id, user=request.user)
        article.user.remove(request.user)
        return Response({"message": f"Article '{article.title}' removed successfully."})


# -- Dictionary -- #
class DictionaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        dictionary = Dictionary.objects.filter(user=request.user).order_by("-date_added")
        serializer = DictionarySerializer(dictionary, many=True)
        return Response(serializer.data)


class AddWordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "word": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["word"],
        ),
    )
    def post(self, request):
        word = request.data.get("word")
        translation = GoogleTranslator(source="auto", target="uk").translate(word)
        dictionary = Dictionary(word=word, translation=translation)
        dictionary.save()
        dictionary.user.add(request.user)  # Associate the word with the current user
        serializer = DictionarySerializer(dictionary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShowWordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        dictionary = Dictionary.objects.get(id=id, user=request.user)
        serializer = DictionarySerializer(dictionary)
        return Response(serializer.data)


class DeleteWordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, id):
        dictionary = Dictionary.objects.get(id=id, user=request.user)
        dictionary.user.remove(request.user)
        return Response({"message": f"Word '{dictionary.word}' removed successfully."})
