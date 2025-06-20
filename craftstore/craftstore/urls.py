from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('', include('user.urls')),
    path('', include('cdn.urls')),
    path('', include('sandbox.urls')),
    path('', include('messenger.urls')),
]
