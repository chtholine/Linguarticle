from django.urls import path

from .views import *

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
    path("articles/<int:pk>/", DetailedArticleView.as_view(), name="show-article"),
    # Dictionary
    path("dictionary/", DictionaryView.as_view(), name="dictionary"),
    path("dictionary/translate/", TranslationView.as_view(), name="translate-word"),
    path("dictionary/<int:pk>/", DetailedDictionaryView.as_view(), name="show-word"),
]
