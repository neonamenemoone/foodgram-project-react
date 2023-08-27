from django.urls import path, re_path, include
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from .views import UserView, TagView

router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'tags', TagView)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    re_path('^auth/', include('djoser.urls.authtoken')),
    path('', UserView.as_view({'get':'me'})),
    path('', UserView.as_view({'post':'set_password'})),
    path('tags/<int:pk>/', TagView.as_view({'get':'get_tag_by_id'}), name='tag-detail'),
]
