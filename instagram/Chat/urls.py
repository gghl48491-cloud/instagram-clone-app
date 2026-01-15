from django.urls import path
from .views import chat_with, send_message, get_messages

urlpatterns = [
    path('<uuid:user_uuid>/', chat_with, name='chat_with'),
    path('<uuid:user_uuid>/send/', send_message, name='send_message'),
    path('<uuid:user_uuid>/get/', get_messages, name='get_messages'),
]