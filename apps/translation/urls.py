from .views import *
from django.urls import path

urlpatterns = [
    # Auth
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    # Settings
    path("settings/username/", UpdateUsernameAPIView.as_view(), name="update-username"),
    path("settings/email/", UpdateEmailAPIView.as_view(), name="update-email"),
    path("settings/password/", UpdatePasswordAPIView.as_view(), name="update-password"),
    # Articles
    path("articles/", ArticlesView.as_view(), name="articles"),
    path("articles/add/", AddArticleView.as_view(), name="add-article"),
    path("articles/<int:id>/", ShowArticleView.as_view(), name="show-article"),
    path("articles/<int:id>/update/", UpdateArticleView.as_view(), name="update-article"),
    path("articles/<int:id>/delete/", DeleteArticleView.as_view(), name="delete-article"),

    path("crawl/", StartCrawlView.as_view(), name="start_crawl"),
    path("add_article/", submit_url, name="add_article"),
]
