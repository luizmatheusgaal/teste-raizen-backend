from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'phone', 'document']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        error_messages={
            'min_length': 'A senha deve ter pelo menos 8 caracteres.',
            'required': 'A senha é obrigatória.',
            'blank': 'A senha é obrigatória.',
        },
    )
    email = serializers.EmailField(
        error_messages={
            'invalid': 'Informe um e-mail válido.',
            'required': 'O e-mail é obrigatório.',
            'blank': 'O e-mail é obrigatório.',
        },
        validators=[UniqueValidator(queryset=User.objects.all(), message='Já existe uma conta com este e-mail.')]
    )
    username = serializers.CharField(
        error_messages={
            'required': 'O nome de usuário é obrigatório.',
            'blank': 'O nome de usuário é obrigatório.',
        },
        validators=[UniqueValidator(queryset=User.objects.all(), message='Este nome de usuário já está em uso.')]
    )
    first_name = serializers.CharField(
        error_messages={'required': 'O nome é obrigatório.', 'blank': 'O nome é obrigatório.', 'max_length': 'O nome é muito longo.'}
    )
    last_name = serializers.CharField(
        error_messages={'required': 'O sobrenome é obrigatório.', 'blank': 'O sobrenome é obrigatório.', 'max_length': 'O sobrenome é muito longo.'}
    )
    role = serializers.ChoiceField(
        choices=User.Role.choices,
        error_messages={'invalid_choice': 'Perfil de acesso inválido.'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'role', 'phone', 'document']

    def validate_password(self, value):
        try:
            validate_password(value)
        except serializers.ValidationError as exc:
            raise serializers.ValidationError('A senha deve conter letras e números e não pode ser muito comum.') from exc
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
