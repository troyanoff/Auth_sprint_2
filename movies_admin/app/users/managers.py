from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, login, password=None):
        if not login:
            raise ValueError("Users must have a login")

        user = self.model(login=login)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None):
        user = self.create_user(login, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user
