from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'

    ROLE_CHOICES = [
        (USER_ROLE, 'Обычный пользователь'),
        (MODERATOR_ROLE, 'Модератор'),
        (ADMIN_ROLE, 'Администратор'),
    ]

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        blank=False
    )

    bio = models.TextField(
        'Биография',
        blank=True
    )

    role = models.CharField(
        'Роль пользователя',
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER_ROLE
    )

    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        blank=True
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == self.ADMIN_ROLE or self.is_superuser

    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE
