"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.translation.views import ArticleView
from .yasg import urlpatterns as doc_urls
from .token_views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


urlpatterns = [
    path("", ArticleView.as_view(), name="article"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.translation.urls")),
    path("api/v1/token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

urlpatterns += doc_urls
