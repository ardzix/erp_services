from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from libs.pagination import CustomPagination
from ..models import File, Configuration
from ..serializers.configuration import ConfigurationSerializer
from ..serializers import FileCreateSerializer, MeSerializer


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MeSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.DjangoModelPermissionsOrAnonReadOnly]
    pagination_class = CustomPagination
    lookup_field = 'key'  # Use the 'key' as the lookup field.

    def get_queryset(self):
        """
        Optionally restricts the returned configurations to a given key,
        by filtering against a `key` query parameter in the URL.
        """
        queryset = self.queryset
        key = self.request.query_params.get('key', None)
        if key is not None:
            queryset = queryset.filter(key=key)
        return queryset
