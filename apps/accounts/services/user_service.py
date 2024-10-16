import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.contrib.auth.hashers import make_password

from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import ValidationError, NotFound

from apps.core.services.email_service import EmailService
from apps.empresas.services.empresa_service import EmpresaService

from apps.accounts.models import User
from apps.accounts.repositories.user_repository import UserRepository
from apps.accounts.services.auth_service import AuthenticationService


class UserService:
    def __init__(self):
        self.repository = UserRepository()

        self.auth_service = AuthenticationService()

        self.email_service = EmailService()
        self.empresa_service = EmpresaService()

    def get_user(self, request=None, user_id=None):
        if user_id is None and request is not None:
            user_id = request.user.id

        try:
            user = self.repository.get_user_by_id(user_id)
            return user
        except User.DoesNotExist:
            raise NotFound('Usuário não encontrado.')

    def get_users_empresa(self, request):
        empresa_id = request.user.empresa.id if request.user.empresa else None

        if empresa_id is None:
            raise ValidationError('O usuário não está associado a nenhuma empresa cadastrada.')
        
        try:
            empresa = self.empresa_service.get_empresa(empresa_id)
            users_empresa = self.repository.get_users_by_empresa(empresa.id)
            
            return users_empresa
        except NotFound:
            raise NotFound('Empresa não encontrada.')

    def get_session(self, user):
        profile_picture_url = user.profile_picture.url if user.profile_picture else None
        empresa = user.empresa.nome if user.empresa else None
        is_solo_admin = user.groups.filter(name='solo_admin').exists()

        return {
            'email': user.email,
            'nome': user.nome,
            'empresa': empresa,
            'is_admin_empresa': user.is_admin_empresa,
            'is_solo_admin': is_solo_admin,
            'profile_picture': profile_picture_url
        }

    def create_user(self, request, **validated_data):
        empresa = request.user.empresa
        group = self.repository.get_group('solo_admin') if not empresa else None
        password_temp = self.repository.generate_password_temp()

        validated_data['empresa'] = empresa
        validated_data['password'] = password_temp

        if self.repository.validate_email(validated_data['email']):
            raise ValidationError('Este e-mail já está em uso.')
        
        user = self.repository.create(group, **validated_data)

        access_token = AccessToken.for_user(user)
        access_token.set_exp(lifetime=timedelta(hours=1))

        self.email_service.send_reset_password_email(access_token, user.email)
        return user

    def update_user(self, user, **validated_data):
        return self.repository.update(user, **validated_data)

    def delete_user(self, user_id):
        user = self.get_user(user_id=user_id)
        self.repository.delete(user)

    def process_email_change(self, user, **validated_data):
        email_atual = validated_data['email_atual']
        email_novo = validated_data['email_novo']

        if email_atual != user.email:
            raise ValidationError('O e-mail atual informado não corresponde ao e-mail cadastrado.')
        
        if self.repository.validate_email(email_novo):
            raise ValidationError('Este e-mail já está em uso.')
        
        try:
            access_token = AccessToken.for_user(user)
            access_token['email_novo'] = email_novo

            access_token.set_exp(lifetime=timedelta(hours=1))
            self.email_service.send_request_email_change(access_token, email_novo)
        except Exception as e:
            raise ValidationError(str(e))
    
    def confirm_email_change(self, request):
        token = self.auth_service.validate_access_token(request)

        user_id = token.get('user_id')
        email_novo = token.get('email_novo')

        if not email_novo:
            raise ValidationError('Toke inválido.')

        user = self.get_user(user_id=user_id)
        return self.repository.update(user, email=email_novo)
    
    def process_password_reset(self, request):
        email = request.data.get('email')

        if not email:
            raise ValidationError({'email': ["Este campo é obrigatório."]})
        
        try:
            user = self.repository.get_user_by_email(email)

            access_token = AccessToken.for_user(user)
            access_token.set_exp(lifetime=timedelta(hours=1))

            self.email_service.send_reset_password_email(access_token, email)
        except User.DoesNotExist:
            raise NotFound('Usuário não encontrado.')
        except Exception as e:
            raise ValidationError(str(e))
    
    def reset_password(self, request):
        token = self.auth_service.validate_access_token(request)

        user_id = token.get('user_id')
        email = token.get('email')
        senha_nova = request.data.get('senha_nova')

        if email:
            raise ValidationError('Token inválido.')

        if not senha_nova:
            raise ValidationError({'senha_nova': ["Este campo é obrigatório."]})
        
        user = self.get_user(user_id=user_id)
        user.password = make_password(senha_nova)

        user.save()