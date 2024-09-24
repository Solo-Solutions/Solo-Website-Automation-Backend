from rest_framework import serializers
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    empresa = serializers.CharField(source='empresa.nome', read_only=True)

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

class UpdateUserSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100, required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())

        for field in data:
            if field not in allowed_fields:
                raise serializers.ValidationError({field: 'Parâmetro inválido.'})
            
        return super().to_internal_value(data)
    
class ChangeEmailSerializer(serializers.Serializer):
    email_atual = serializers.EmailField(required=True)
    email_novo = serializers.EmailField(required=True)

    def to_internal_value(self, data):
        allowed_fields = set(self.fields.keys())

        for field in data:
            if field not in allowed_fields:
                raise serializers.ValidationError({field: 'Parâmetro inválido.'})
            
        return super().to_internal_value(data)