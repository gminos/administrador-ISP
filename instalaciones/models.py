from django.db import models


class Intalacion(models.Model):
    instalacion_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario",
        null=True,
        on_delete=models.SET_NULL,
        related_name="instalacion"
    )
    fecha_instalacion = models.DateTimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    plan = models.ForeignKey(
        "planes.Plan",
        on_delete=models.SET_NULL,
        null=True,
        related_name='instalaciones'
    )
    servicio_activo = models.BooleanField(default=True, null=True)

    class Meta:
        verbose_name = "instalacion a cliente"
        verbose_name_plural = "informacion de instalaciones"

    def __str__(self):
        return f"Informacion de {self.usuario.nombre} {self.usuario.apellido}"
