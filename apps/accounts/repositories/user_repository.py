from ..models import User


class UserRepository:
    def get_user_by_id(self, user_id):
        return User.objects.get(id=user_id)

    def get_users_by_empresa(self, empresa_id):
        return User.objects.filter(empresa_id=empresa_id).order_by('-date_joined')
    
    def create(self, **validated_data):
        return User.objects.create_user(**validated_data)
    
    def update(self, user, **validated_data):
        if 'profile_picture' in validated_data:
            if validated_data['profile_picture'] is None:
                user.profile_picture.delete(save=False)
                user.profile_picture = None
                
        for key, value in validated_data.items():
            setattr(user, key, value)
        
        user.save()
        return user

    def validate_email(self, email):
        return User.objects.filter(email=email).exists()
    
    def generate_password_temp(self):
        return User.objects.make_random_password()