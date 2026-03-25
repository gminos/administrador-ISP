from django.db import models


class CicloFacturacionChoices(models.IntegerChoices):
    QUINCENA = 15, "Quincenal"
    MENSUAL = 30, "Mensual"


class Instalacion(models.Model):
    instalacion_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.CASCADE,
        related_name="instalaciones"
    )
    fecha_instalacion = models.DateTimeField()
    costo = models.DecimalField(max_digits=10, decimal_places=2)
    plan = models.ForeignKey(
        "planes.Plan",
        on_delete=models.SET_NULL,
        null=True,
        related_name='instalaciones'
    )
    servicio_activo = models.BooleanField(default=True)
    ciclo_facturacion = models.IntegerField(choices=CicloFacturacionChoices.choices, default=CicloFacturacionChoices.MENSUAL)

    class Meta:
        verbose_name = "instalacion"
        verbose_name_plural = "instalaciones"

    def __str__(self):
        return f"{self.cliente.nombre} {self.cliente.apellido}"
