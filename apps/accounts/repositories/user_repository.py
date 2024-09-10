from ..models import User


class UserRepository:
    def create(self, **kwargs):
        return User.objects.create_user(**kwargs)
    
    def validate_email(self, email):
        return User.objects.filter(email=email).exists()
    
    def generate_password_temp(self):
        return User.objects.make_random_password()
    
    def get_users_by_empresa(self, empresa_id):
        return User.objects.filter(empresa_id=empresa_id).order_by('-date_joined')
    