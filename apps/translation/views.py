import os
import nltk
from deep_translator import GoogleTranslator
import subprocess
from django.views import View
from drf_yasg import openapi
import requests
from bs4 import BeautifulSoup
from drf_yasg.utils import swagger_auto_schema
from nltk import word_tokenize
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer, DictionarySerializer, ArticleUpdateSerializer
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Article, Dictionary
from .serializers import ArticleSerializer
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404


def url_valid(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False
    return True


class ArticleView(View):
    def get(self, request):
        articles = Article.objects.order_by("date_added")
        return render(request, "home.html", {"articles": articles, "user": request.user})


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

        # add scrapy dir to python path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scraper_dir = os.path.join(base_dir, "scraper")
        os.environ["PYTHONPATH"] = scraper_dir
        # os.environ["PYTHONPATH"] = "/home/chtholine/PycharmProjects/django_translation/scraper"
        # launch scrapy spider with subprocess
        spider_name = "article_spider"
        user_id = request.user.id
        command = f"scrapy crawl {spider_name} -a url={canonical_url} -a user_id={user_id}"
        try:
            subprocess.run(
                command.split(), check=True, cwd=scraper_dir
            )  # the response will not be returned until this method finishes scraping process
            # article = Article.objects.get(url=canonical_url)
            # content = article.data
            # parts = [content[i : i + 4000] for i in range(0, len(content), 4000)]
            # translated_parts = []
            # for part in parts:
            #     translated_part = GoogleTranslator(source="auto", target="uk").translate(part)
            #     translated_parts.append(translated_part)
            # translated_content = "".join(translated_parts)
            # article.translation = translated_content
            # article.save()
            return Response({"message": f"{spider_name} spider has parsed: {canonical_url}"})
            # return redirect("articles")  # you can get articles json after parsing
        except subprocess.CalledProcessError as e:
            return Response({"error": str(e)}, status=500)


class DetailedArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk, user=request.user)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ArticleUpdateSerializer)
    def put(self, request, pk):
        article = Article.objects.get(pk=pk, user=request.user)
        serializer = ArticleUpdateSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = Article.objects.get(pk=pk, user=request.user)
        article.user.remove(request.user)
        return Response({"message": f"Article '{article.title}' removed successfully."})


# -- Dictionary -- #
class DictionaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        dictionary = Dictionary.objects.filter(user=request.user).order_by("-date_added")
        serializer = DictionarySerializer(dictionary, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "word": openapi.Schema(type=openapi.TYPE_STRING),
                "translation": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["word", "translation"],
        ),
    )
    def post(self, request):
        word = request.data.get("word")
        translation = request.data.get("translation")
        dictionary = Dictionary(word=word, translation=translation)
        dictionary.save()
        dictionary.user.add(request.user)  # Associate the word with the current user
        serializer = DictionarySerializer(dictionary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TranslationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        return Response({"word": word, "translation": translation})


class DetailedDictionaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        dictionary = Dictionary.objects.get(pk=pk, user=request.user)
        serializer = DictionarySerializer(dictionary)
        return Response(serializer.data)

    def delete(self, request, pk):
        dictionary = Dictionary.objects.get(pk=pk, user=request.user)
        dictionary.user.remove(request.user)
        return Response({"message": f"Word '{dictionary.word}' removed successfully."})
