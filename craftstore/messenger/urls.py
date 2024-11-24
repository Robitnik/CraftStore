from django.urls import path
from . import views


urlpatterns = [
    path("api/rest/messeger", views.UserChatSet.as_view()),
    path("api/rest/messeger/chat/<str:slug>", views.ChatMessageSet.as_view()),
]
