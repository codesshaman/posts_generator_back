from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, login, email, auth, password=None, **extra_fields):
        if not auth:
            raise ValueError(_('The auth field must be set'))
        if not login:
            raise ValueError(_('The login field must be set'))
        if email:
            email = self.normalize_email(email)
            # Проверка уникальности email только если email не пустой
            if User.objects.filter(email=email).exists():
                raise ValueError(_('This email is already taken.'))
        user = self.model(login=login, email=email, auth=auth, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Передаем все аргументы как именованные
        return self.create_user(
            login=login,
            email=email,
            auth="email",
            password=password,
            **extra_fields
        )

class User(AbstractBaseUser, PermissionsMixin):
    AUTH_CHOICES = [
        ('email', 'Email'),
        ('vk', 'VK'),
        ('google', 'Google'),
    ]

    email = models.EmailField(unique=True, blank=True, null=True)
    login = models.CharField(max_length=150, unique=True)
    auth = models.CharField(max_length=10, choices=AUTH_CHOICES, default='email')
    vk = models.BigIntegerField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=150, blank=True)
    surname = models.CharField(max_length=150, blank=True)
    referrer = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=now, verbose_name=_("date joined"))

    USERNAME_FIELD = "login"
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.login

    # Уникальные related_name для групп и разрешений
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name=_("groups"),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
    )

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_active = True  # Устанавливаем is_active в True для суперпользователей
        if self.auth != "email":
            self.is_active = True
        super().save(*args, **kwargs)

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.login
