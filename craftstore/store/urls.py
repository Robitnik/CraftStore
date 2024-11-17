from django.urls import path
from . import views


urlpatterns = [
    path("", views.main, name="home"),
    path("api/rest/goods/filter", views.GoodsViewSet.as_view(), name="lasted_url")
]
