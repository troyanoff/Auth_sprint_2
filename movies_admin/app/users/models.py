import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from users.managers import MyUserManager


class User(AbstractBaseUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.CharField(verbose_name="login", max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    # строка с именем поля модели, которая используется в качестве уникального идентификатора
    USERNAME_FIELD = "login"

    # менеджер модели
    objects = MyUserManager()

    def __str__(self):
        return f"{self.login} {self.id}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
