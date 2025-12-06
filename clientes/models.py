from django.db import models


class Cliente(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10, blank=True)
    vereda = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
