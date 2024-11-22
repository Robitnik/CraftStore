from django.urls import path
from . import views


urlpatterns = [
    path("root/sandbox", views.sand_box, name="sandbox_url"),
]
