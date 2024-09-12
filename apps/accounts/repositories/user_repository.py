from ..models import User


class UserRepository:
    def create(self, **kwargs):
        return User.objects.create_user(**kwargs)
    
    def update(self, user, **kwargs):
        for key, value in kwargs.items():
            setattr(user, key, value)
        
        user.save()
        return user

    def validate_email(self, email):
        return User.objects.filter(email=email).exists()
    
    def generate_password_temp(self):
        return User.objects.make_random_password()
    
    def get_user_by_id(self, user_id):
        return User.objects.get(id=user_id)

    def get_users_by_empresa(self, empresa_id):
        return User.objects.filter(empresa_id=empresa_id).order_by('-date_joined')
    