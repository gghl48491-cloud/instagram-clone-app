from django.urls import path, include
from .views import me, profile
from Interactions.views import toggle_follow

urlpatterns = [
    path("me/", me, name="me"),
    path("profile/<uuid:user_uuid>/", profile, name="profile"),
    path("profile/<uuid:user_uuid>/follow", toggle_follow, name="toggle_follow"),
    path("", include("allauth.urls")),
]
