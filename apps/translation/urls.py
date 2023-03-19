from . import views
from django.urls import path

urlpatterns = [
    path("parse", views.ScrapingView.as_view(), name="parse")
]
