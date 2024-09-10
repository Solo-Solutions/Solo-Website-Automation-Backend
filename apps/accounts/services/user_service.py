import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from rest_framework.exceptions import ValidationError

from core.services.email_service import EmailService
from apps.accounts.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()
        self.email_service = EmailService()

    def create_user(self, request, **kwargs):
        empresa = request.user.empresa
        password_temp = self.repository.generate_password_temp()

        kwargs['empresa'] = empresa
        kwargs['password'] = password_temp

        self.validate_fields(**kwargs)
        user = self.repository.create(**kwargs)

        try:
            payload_token = {
                'user_id': str(user.id),
                'email': user.email,
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            }
            token = jwt.encode(payload_token, settings.SECRET_KEY, algorithm='HS256')

            self.email_service.send_reset_password_email(token, user.email)
        except Exception as e:
            raise ValidationError(str(e))
        
        return user
    
    def get_users_by_empresa(self, request):
        empresa_id = request.user.empresa.id

        users_empresa = self.repository.get_users_by_empresa(empresa_id)
        return users_empresa

    @staticmethod
    def validate_fields(**kwargs):
        email = kwargs.get('email')

        if UserRepository().validate_email(email):
            raise ValidationError('O e-mail informado já possui um usuário cadastrado.')