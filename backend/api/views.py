from users.models import User
from recipes.models import Tag, Ingredient
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import SearchFilter


from .serializers import UserProfileSerializer, UserRegistrationSerializer, UserSetPasswordSerializer, TagSerializer, IngredientSerializer, UserWithSubscriptionsSerializer


class UserView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny] 

    def create(self, request):
        serializer = UserRegistrationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request)

    def perform_update(self, serializer):
        serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        response_data = {
            'count': len(data),
            'next': None,
            'previous': None,
            'results': data,
        }
        return Response(response_data)
    
    def retrieve(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated]
        self.check_permissions(request)
        return super().retrieve(request)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        return Response(UserProfileSerializer(request.user).data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.check_password(serializer.validated_data['current_password']):
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError('Текущий пароль неверный.')


class TagView(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

    
class IngredientView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']


class SubscriptionsView(viewsets.ModelViewSet):
    serializer_class = UserWithSubscriptionsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.subscriptions.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        response_data = {
            'count': len(data),
            'next': None,
            'previous': None,
            'results': data,
        }
        return Response(response_data)
