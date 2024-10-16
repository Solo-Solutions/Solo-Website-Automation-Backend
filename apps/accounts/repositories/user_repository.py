from ..models import User
from django.contrib.auth.models import Group


class UserRepository:
    def get_user_by_id(self, user_id):
        return User.objects.get(id=user_id)

    def get_user_by_email(self, email):
        return User.objects.get(email=email)

    def get_users_by_empresa(self, empresa_id):
        return User.objects.filter(empresa_id=empresa_id).order_by('-date_joined')
    
    def get_group(self, group_name):
        return Group.objects.get(name=group_name)

    def create(self, group=None, **validated_data):
        user = User.objects.create_user(**validated_data)

        if group:
            user.groups.add(group)
            user.save()
            
        return user
    
    def update(self, user, **validated_data):
        if 'profile_picture' in validated_data:
            if validated_data['profile_picture'] is None:
                user.profile_picture.delete(save=False)
                user.profile_picture = None
                
        for key, value in validated_data.items():
            setattr(user, key, value)
        
        user.save()
        return user

    def delete(self, user):
        user.delete()

    def validate_email(self, email):
        return User.objects.filter(email=email).exists()
    
    def generate_password_temp(self):
        return User.objects.make_random_password()