from django.urls import path
from . import views


urlpatterns = [
    path("api/rest/user/login", views.UserLogin.as_view(), name="user_login_url"),
    path("api/rest/user/logout", views.UserLogout.as_view(), name="user_logout_url"),
    path("api/rest/user/register", views.UserRegister.as_view(), name="user_register_url"),
    path("api/rest/user/edit", views.UserEdit.as_view(), name="user_edit_url"),
    path("api/rest/user/reset/password", views.UserResetPassword.as_view(), name="user_reset_password_url"),
    path("api/rest/user", views.User.as_view(), name="user_url"),
    path("api/rest/user/favorites", views.UserFavoritesAPI.as_view(), name="user_favorites_url"),
    path("api/rest/user/history", views.UserHistoryAPI.as_view(), name="user_history_url"),
    path("api/rest/user/cart", views.UserCartAPI.as_view(), name="user_history_url"),
    path("api/rest/user/login/csrf", views.UserCsrf.as_view(), name="user_csrf_url"),
]
