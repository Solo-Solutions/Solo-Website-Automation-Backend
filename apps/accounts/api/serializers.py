from rest_framework import serializers
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nome', 'empresa', 'date_joined', 'profile_picture']

class CreateUserSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100, required=False, default="Membro")
    email = serializers.EmailField(required=True)

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())

        for field in data:
            if field not in allowed_fields:
                raise serializers.ValidationError({field: 'Parâmetro inválido.'})
            
        return super().to_internal_value(data)

class UpdateUserNameSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['nome']

    def update(self, instance, validated_data):
        nome = validated_data.get('nome')
        instance.nome = nome

        instance.save()
        return instance

class UpdateProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ['profile_picture']

    def update(self, instance, validated_data):
        profile_picture = validated_data.get('profile_picture')
        instance.profile_picture = profile_picture

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.profile_picture:
            request = self.context.get('request')
            representation['profile_picture_url'] = request.build_absolute_uri(instance.profile_picture.url)
        else:
            representation['profile_picture_url'] = None

        return representation
    
class DeleteProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_picture']

    def update(self, instance, validated_data):
        if instance.profile_picture:
            instance.profile_picture.delete(save=False)
            instance.profile_picture = None

            instance.save()
        else:
            raise serializers.ValidationError({'detail': 'O usuário não possui foto de perfil para excluir.'})
        
        return instance