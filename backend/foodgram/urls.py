"""foodgram URL Configuration."""

from rest_framework.authtoken import views

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
