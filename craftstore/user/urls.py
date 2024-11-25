from django.urls import path
from . import views


urlpatterns = [
    path("api/rest/user/login", views.UserLogin.as_view(), name="user_login_url"),
    path("api/rest/user/register", views.UserRegister.as_view(), name="user_register_url"),
    path("api/rest/user/edit", views.UserEdit.as_view(), name="user_edit_url"),
    path("api/rest/user/reset/password", views.UserResetPassword.as_view(), name="user_reset_password_url"),
    path("api/rest/user", views.User.as_view(), name="user_url"),
    path("api/rest/user/favorites", views.FavoritesAPI.as_view(), name="user_favorites_url"),

]
