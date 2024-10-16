from rest_framework.exceptions import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


class AuthenticationService:
    def refresh_access_token(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            raise ValidationError('Refresh token não encontrado.')
        
        try:
            refresh = RefreshToken(refresh_token)
            access = refresh.access_token

            return access
        except TokenError:
            raise ValidationError('Token inválido.')

    def validate_access_token(self, request):
        token = request.data.get('token')

        if not token:
            raise ValidationError('Token não encontrado.')
        
        try:
            access_token = AccessToken(token)
            return access_token
        except (InvalidToken, TokenError) as e:
            raise ValidationError(f"Token inválido: {str(e)}")

    def logout(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            raise ValidationError('Refresh token não encontrado.')
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise ValidationError('Token inválido.')