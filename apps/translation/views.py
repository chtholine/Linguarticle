from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

from scraper.scraper.spiders.myspider import ArticleSpider
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Article
from .serializers import ArticleSerializer
from django.views.decorators.http import require_POST, require_http_methods
from scrapyd_api import ScrapydAPI
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from twisted.internet import reactor
from django.shortcuts import render
from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from django.http import JsonResponse
from django.views import View

setup()  # Initialize crochet


class StartCrawlView(View):
    @wait_for(timeout=10.0)  # Set a timeout for the crawl operation
    def run_crawl(self, url):
        runner = CrawlerRunner()
        return runner.crawl(ArticleSpider, start_url=url)

    def post(self, request, *args, **kwargs):
        url = request.POST.get('url')
        self.run_crawl(url)  # Run the crawl operation
        return JsonResponse({"status": "success"})


# connect scrapyd service
scrapyd = ScrapydAPI("http://localhost:6800")


def submit_url(request):
    return render(request, 'add_article.html')


def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)  # check if url format is valid
    except ValidationError:
        return False

    return True


# --- Auth --- #
class SignUpAPIView(APIView):
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

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

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Username updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateEmailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Email updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        articles = Article.objects.filter(user=request.user)
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class AddArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        article = Article.objects.get(id=id, user=request.user)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)


class UpdateArticleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        article.delete()
        return Response({"message": f"Article '{article.title}' deleted successfully."})
