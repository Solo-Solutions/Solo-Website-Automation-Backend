from django.core.mail import send_mail

from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from ..models import Empresa
from apps.accounts.utils import generate_reset_password_token
from apps.empresas.services.empresa_service import EmpresaService

from apps.core.permissions import IsSoloAdmin
from .serializers import EmpresaSerializer, EmpresaCreateSerializer, EmpresaUpdateSerializer


class CustomPagePagination(PageNumberPagination):
    page_size = 7
    page_query_param = 'page'
    max_page_size = 50

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSoloAdmin])
def get_list_empresas(request):
    service = EmpresaService()
    pagination_class = CustomPagePagination()

    try:
        empresas = service.get_list_empresas()

        paginated_queryset = pagination_class.paginate_queryset(empresas, request)
        serializer = EmpresaSerializer(paginated_queryset, many=True)

        response = pagination_class.get_paginated_response({
            "empresas": serializer.data
        })

        response.status_code = status.HTTP_200_OK
        return response
    except NotFound as e:
        return Response({'detail': str(e.detail)}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSoloAdmin])
def create_empresa(request):
    serializer = EmpresaCreateSerializer(data=request.data)

    if serializer.is_valid():
        empresa = serializer.save()

        email = request.data.get('email')
        token = generate_reset_password_token(email)

        reset_link = f"http://localhost:3000/reset-password?token={token}"
        send_mail(
            'Redefinição de Senha',
            f'Clique no link para redefinir sua senha: {reset_link}',
            'noreply@solosolutions.com.br',
            [email],
            fail_silently=False,
        )

        empresa_serializer = EmpresaSerializer(empresa, many=False)
        return Response({'empresa': empresa_serializer.data}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSoloAdmin])
def update_empresa(request, id):
    service = EmpresaService()

    try:
        empresa = service.get_empresa(id)
        serializer = EmpresaUpdateSerializer(instance=empresa, data=request.data, partial=True)

        if serializer.is_valid():
            updated_empresa = service.update_empresa(empresa, **serializer.validated_data)
            empresa_serializer = EmpresaSerializer(updated_empresa, many=False)

            return Response({'empresa': empresa_serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except NotFound:
        return Response({'detail': 'Empresa não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'detail': str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_empresa_by_name(request):
    nome = request.query_params.get('nome')
    if nome:
        try:
            empresa = Empresa.objects.get(nome=nome)
            empresa.delete()
            return Response({'detail': 'Empresa deletada com sucesso.'}, status=status.HTTP_204_NO_CONTENT)
        except Empresa.DoesNotExist:
            return Response({'detail': 'Empresa não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': 'Nome não fornecido'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def api_overview(request):
    api_urls = [
        '/api/empresas/',

        '/api/empresas/list-empresas/',
        '/api/empresas/create-empresa',
        '/api/empresas/delete-by-name/'
    ]

    return Response(api_urls)