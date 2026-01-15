from django.urls import path
from .views import Create, Update, Delete, List, ListDetail

from Comments.views import add, get
from Interactions.views import toggle_like, toggle_dislike, toggle_comment_like

urlpatterns = [
    path("", List, name="list"),
    path("create/", Create, name="create"),
    path("<uuid:id>/update", Update, name="update"),
    path("<uuid:id>/delete", Update, name="delete"),
    path("<uuid:id>/", ListDetail),
    path("<uuid:id>/comment/add", add, name="add_comment"),
    path("<uuid:id>/comment/get", get, name="get_comment"),
    path("<uuid:id>/like", toggle_like, name="post_like"),
    path("<uuid:id>/dislike", toggle_dislike, name="post_dislike"),
    path("comment/<int:comment_id>/like", toggle_comment_like, name="comment_like"),
]
