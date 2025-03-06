from django.urls import path
from . import views


urlpatterns = [
    path("", views.main, name="home"),
    path("test", views.Test.as_view(), name="test"),
    path("api/rest/goods/filter", views.GoodsViewFilter.as_view(), name="lasted_url"),
    path("api/rest/user/owner/store", views.UserStore.as_view(), name="user_store_create_url"),
    path("api/rest/store/filter", views.StoreViewSet.as_view(), name="store_filter_url"),
    path("api/rest/user/owner/store/goods", views.StoreGoodSet.as_view(), name="store_filter_url"),
    path("api/rest/store/<str:store_slug>/goods/<str:goods_slug>", views.StoreGoodSet.as_view(), name="store_filter_url"),
    path("api/rest/goods", views.StoreGoodSet.as_view(), name="store_filter_url"),
    path("api/rest/goods/<int:goods_id>", views.StoreGoodSet.as_view(), name="store_filter_url"),
    path("api/rest/goods/<int:goods_id>/reviews", views.GoodsReviewViewSet.as_view(), name="goods_reviews_url"),
    path("api/rest/reviews/<int:review_id>", views.ReviewViewSet.as_view(), name="reviews_url"),
    path("api/rest/categories/filter", views.CategoryViewSet.as_view(), name="categories_filter_url"),
]