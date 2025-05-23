from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("search/", views.search_results, name="search_results"),
]
