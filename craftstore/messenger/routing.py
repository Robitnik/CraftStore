from django.urls import path
from . import consumers


ws_urlpatterns = [
    path("api/ws/chat/<str:chat_slug>/<str:user_token>", consumers.ChatConsumer.as_asgi())
]