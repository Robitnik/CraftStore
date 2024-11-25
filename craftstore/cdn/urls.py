from django.urls import path
from . import views


urlpatterns = [
    path("api/rest/cdn/image/upload", views.ImageSet.as_view(), name="upload_img_url"),
    path("api/rest/cdn/image/delete", views.ImageSet.as_view(), name="delete_img_url")
]
