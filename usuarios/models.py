from django.db import models


# tabla usuarios. por defecto defecto los campos son not null (no hay que expecificar)
class Usuarios(models.Model):
    documento = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nombre} {self.apellido} {self.apellido}"
