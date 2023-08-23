from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserListView

router = DefaultRouter()
router.register(r'users', UserListView)

urlpatterns = [
    path('', include(router.urls)),
]