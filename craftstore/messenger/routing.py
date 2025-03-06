from django.urls import path
from . import consumers


ws_urlpatterns = [
    path("api/ws/chat/<str:user_token>/<str:chat_slug>", consumers.ChatConsumer.as_asgi())
]