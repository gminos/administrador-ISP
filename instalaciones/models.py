from django.db import models


class Intalacion(models.Model):
    instalacion_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="instalacion"
    )
    fecha_instalacion = models.DateTimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "instalacion a cliente"
        verbose_name_plural = "agregar instalacion a cliente"

    def __str__(self):
        return f"Informacion de {self.usuario.nombre} {self.usuario.apellido}"
