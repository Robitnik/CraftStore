from django.urls import path
from . import views


urlpatterns = [
    path("", views.main, name="home"),
    path("api/rest/goods/filter", views.GoodsViewSet.as_view(), name="lasted_url"),
    path("api/rest/user/owner/store", views.UserStore.as_view(), name="user_store_create_url"),
    path("api/rest/store/filter", views.StoreViewSet.as_view(), name="store_filter_url"),
]