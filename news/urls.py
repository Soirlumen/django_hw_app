from django.urls import path
from .views import posts_view, create_post_view,edit_post_view

urlpatterns = [
     path("", posts_view, name="news-post"),
     path("create/", create_post_view, name="create-news-post"),
     path("<int:pk>/edit/",edit_post_view,name="edit-news-post")
]
