from django.urls import path, re_path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from .views import UserListView

router = DefaultRouter()
router.register(r'users', UserListView)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    re_path('^auth/', include('djoser.urls.authtoken')),
    path('', UserListView.as_view({'get':'me'})),
    path('', UserListView.as_view({'post':'set_password'})),
]
