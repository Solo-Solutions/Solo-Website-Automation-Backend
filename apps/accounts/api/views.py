from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserSerializer, CreateUserSerializer, UpdateUserSerializer, ChangeEmailSerializer

from core.permissions import IsAdminEmpresa
from apps.accounts.services.user_service import UserService
from apps.accounts.services.authentication_service import AuthenticationService


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nome'] = user.nome

        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError({'detail': 'Email ou senha inválido.'})
        
        return super().validate(attrs)
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = serializer.validated_data.get('refresh')
        access = serializer.validated_data.get('access')

        response = Response({
            'access': access,
            'refresh': refresh
        })

        response.set_cookie(
            key='access_token',
            value=access,
            httponly=True,
            secure=True,
            samesite='None'
        )

        response.set_cookie(
            key='refresh_token',
            value=refresh,
            httponly=True,
            secure=True,
            samesite='None'
        )

        return response

class CustomPagePagination(PageNumberPagination):
    page_size = 7
    page_query_param = 'page'
    max_page_size = 50

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_access_token(request):
    service = AuthenticationService()

    try:
        access = service.refresh_access_token(request)

        response = Response({'access_token': str(access)}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=str(access),
            httponly=True,
            secure=True,
            samesite='None'
        )

        return response
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    service = AuthenticationService()

    try:
        service.logout(request)
        return Response({'detail': 'Logout successful.'}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminEmpresa])
def create_user(request):
    serializer = CreateUserSerializer(data=request.data)

    if serializer.is_valid():
        service = UserService()
        
        try:
            user = service.create_user(request, **serializer.validated_data)
            user_serializer = UserSerializer(user, many=False)

            return Response({'user': user_serializer.data}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'detail': str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request):
    service = UserService()

    try:
        user = service.get_user(request)
        serializer = UpdateUserSerializer(instance=user, data=request.data, partial=True)

        if serializer.is_valid():
            updated_user = service.update_user(user, **serializer.validated_data)
            user_serializer = UserSerializer(updated_user, many=False)

            return Response({'user': user_serializer.data}, status=status.HTTP_200_OK)
        
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except NotFound as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_email_change(request):
    service = UserService()

    try:
        user = service.get_user(request)
        serializer = ChangeEmailSerializer(data=request.data)

        if serializer.is_valid():
            service.process_email_change(user, **serializer.validated_data)
            return Response({'detail': 'E-mail de confirmação enviado com sucesso.'}, status=status.HTTP_200_OK)
        
        return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except NotFound as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])  
def confirm_email_change(request):
    service = UserService()

    try:
        token = service.validate_token(request)

        updated_user = service.confirm_email_change(token)
        user_serializer = UserSerializer(updated_user, many=False)

        return Response({'user': user_serializer.data}, status=status.HTTP_200_OK)
    except NotFound as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def request_password_reset(request):
    service = UserService()

    try:
        service.process_password_reset(request)
        return Response({'detail': 'Email de redefinição de senha enviado com sucesso.'}, status=status.HTTP_200_OK)
    except NotFound as e:
        return Response({'detail': str(e.detail)}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        if isinstance(e.detail, dict):
            error_detail = {'detail': e.detail}
        else:
            error_detail = {'detail': str(e.detail[0])}

        return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def reset_password(request):
    service = UserService()

    try:
        token = service.validate_token(request)
        service.reset_password(request, token)

        return Response({'detail': 'Senha atualizada com sucesso.'}, status=status.HTTP_200_OK)
    except NotFound as e:
        return Response({'detail': str(e.detail)}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': e.detail}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminEmpresa])
def get_users_empresa(request):
    try:
        service = UserService()
        users_empresa = service.get_users_empresa(request)

        pagination_class = CustomPagePagination()
        paginated_queryset = pagination_class.paginate_queryset(users_empresa, request)

        serializer = UserSerializer(paginated_queryset, many=True)
        response = pagination_class.get_paginated_response({'users': serializer.data})

        response.status_code = status.HTTP_200_OK
        return response
    except NotFound as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_session(request):
    service = UserService()

    try:
        user = service.get_user(request)
        user_session = service.get_session(user)

        return Response({'user': user_session}, status=status.HTTP_200_OK)
    except NotFound as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_overview(request):
    routes = [
        '/api/accounts/'
        '/api/accounts/token/',
        '/api/accounts/token/refresh/',
        '/api/token/logout/',
        '/api/accounts/token/get-user-session/',
        '/api/accounts/create-user/',
        '/api/accounts/update-user/',
        '/api/accounts/request-email-change/',
        '/api/accounts/confirm-email-change/',
        '/api/accounts/request-password-reset/',
        '/api/accounts/reset-password',
        '/api/accounts/get-users-empresa',
    ]

    return Response(routes)