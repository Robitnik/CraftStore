from django.urls import path
from . import views


urlpatterns = [
    path("root/sandbox", views.sand_box, name="sandbox_url"),
    path("root/sandbox/ws", views.ws_sand_box),
    path("root/sandbox/ws/chat/<str:slug>", views.ws_chat_sand_box),
]
