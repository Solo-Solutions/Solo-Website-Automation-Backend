import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone
from rest_framework.exceptions import ValidationError

from .models import User


def generate_reset_password_token(email):
    user = User.objects.filter(email=email).first()

    if not user:
        raise ValidationError('Usuário não encontrado.')
    
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def validate_jwt_token(request):
    token = request.data.get('token')

    if not token:
        raise ValidationError('Token não encontrado.')

    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValidationError('O token expirou.')
    except jwt.InvalidTokenError:
        raise ValidationError('Token inválido.')

def generate_temp_password():
    return User.objects.make_random_password(length=10)