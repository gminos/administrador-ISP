from django.db import models


class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10, blank=True)
    vereda = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def informacion_plan(self):
        return self.instalacion.filter(servicio_activo=True).first().plan

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "Agrega o modifica clientes"
