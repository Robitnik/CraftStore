from django.urls import path
from . import consumers


ws_urlpatterns = [
    path("api/ws/chat/<str:chat_slug>", consumers.WSConsumer.as_asgi())
]