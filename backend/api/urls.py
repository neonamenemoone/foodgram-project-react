from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import UserView, TagView, IngredientView, RecipeView

router = DefaultRouter()
router.register(r'users', UserView)
router.register(r'tags', TagView)
router.register(r'ingredients', IngredientView, basename='ingredient')
router.register(r'recipes', RecipeView)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    re_path('^auth/', include('djoser.urls.authtoken')),
    path('', UserView.as_view({'get':'me'})),
    path('', UserView.as_view({'post':'set_password'})),
    path('', UserView.as_view({'get':'subscriptions'})),
    path('<int:pk>/subscribe/', UserView.as_view({'post': 'subscribe', 'delete': 'subscribe'}), name='subscribe'),
    path('<int:pk>/favorite/', RecipeView.as_view({'post': 'favorite'}), name='favorite'),
    path('<int:pk>/recipes/', RecipeView.as_view({'post': 'create'}), name='create_recipe'),
]
