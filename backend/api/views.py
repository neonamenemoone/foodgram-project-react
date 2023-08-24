from users.models import User
from .serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class UserListView(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    http_method_names = 'get', 'post', 'patch', 'delete'
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = []
    permission_classes = [AllowAny] 

    def perform_create(self, serializer):
        serializer.save()

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
