import re

from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для операций с пользователями."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для endpoint /me/ - без поля role"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio'
        )


class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя."""

    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.CharField(required=True, max_length=150)

    def validate_username(self, value):
        """Проверяет корректность имени пользователя."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено'
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Недопустимые символы в username'
            )
        return value

    def validate(self, data):
        return data


class UserTokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        """Проверяет наличие обязательных полей."""
        if not data.get('username'):
            raise serializers.ValidationError('Username обязателен')
        if not data.get('confirmation_code'):
            raise serializers.ValidationError('Код подтверждения обязателен')
        return data
