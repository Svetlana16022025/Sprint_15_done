import random

from django.core.mail import send_mail
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .permissions import IsAdmin
from .serializers import (
    UserSerializer, UserSignUpSerializer, UserTokenSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователей (только для администраторов)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_me(self, request):
        """Получение и изменение своего профиля"""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        data = request.data.copy()
        if not request.user.is_admin() and 'role' in data:
            del data['role']

        serializer = self.get_serializer(
            request.user,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AuthViewSet(viewsets.ViewSet):
    """Вьюсет для аутентификации"""
    permission_classes = (AllowAny,)

    def generate_confirmation_code(self):
        """Генерация 6-значного кода подтверждения"""
        return str(random.randint(100000, 999999))

    @action(methods=['post'], detail=False, url_path='signup')
    def signup(self, request):
        """Регистрация нового пользователя"""
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']

        user = User.objects.filter(
            username=username,
            email=email
        ).first()

        if user:
            confirmation_code = self.generate_confirmation_code()
            user.confirmation_code = confirmation_code
            user.save()

            send_mail(
                'Новый код подтверждения для YaMDb',
                f'Ваш новый код подтверждения: {confirmation_code}',
                'yamdb@example.com',
                [email],
                fail_silently=False,
            )

            return Response(
                {'email': email, 'username': username},
                status=status.HTTP_200_OK
            )

        if User.objects.filter(email=email).exclude(username=username).exists():
            return Response(
                {'error': 'Пользователь с таким email уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username).exclude(email=email).exists():
            return Response(
                {'error': 'Пользователь с таким username уже существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=None
        )

        confirmation_code = self.generate_confirmation_code()
        user.confirmation_code = confirmation_code
        user.save()

        send_mail(
            'Код подтверждения для YaMDb',
            f'Ваш код подтверждения: {confirmation_code}',
            'yamdb@example.com',
            [email],
            fail_silently=False,
        )

        return Response(
            {'email': email, 'username': username},
            status=status.HTTP_200_OK
        )

    @action(methods=['post'], detail=False, url_path='token')
    def token(self, request):
        """Получение JWT токена"""
        serializer = UserTokenSerializer(data=request.data)
        if not serializer.is_valid():
            if 'username' not in serializer.validated_data:
                return Response(
                    {'error': 'Username обязателен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            return Response(
                {'error': 'Неверный код подтверждения'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)

        return Response({'token': str(token)}, status=status.HTTP_200_OK)
