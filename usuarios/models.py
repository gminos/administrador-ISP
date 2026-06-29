from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email or self.username
