from django.db import models


class Intalacion(models.Model):
    instalacion_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="instalacion"
    )
    fecha_instalacion = models.DateTimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "instacion"
        verbose_name_plural = "Instalaciones"
