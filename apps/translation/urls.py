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
    # Dictionary
    path("dictionary/", DictionaryView.as_view(), name="dictionary"),
    path("dictionary/add/", AddWordView.as_view(), name="add-word"),
    path("dictionary/<int:id>/", ShowWordView.as_view(), name="show-word"),
    path("dictionary/<int:id>/delete/", DeleteWordView.as_view(), name="show-word"),
    # Non-API
    path("add_article/", submit_url, name="add_article"),
]
