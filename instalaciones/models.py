from django.db import models


class CicloFacturacionChoices(models.IntegerChoices):
    QUINCENA = 15, "Quincenal"
    MENSUAL = 30, "Mensual"


class Instalacion(models.Model):
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
        plan_nombre = self.plan.nombre if self.plan else "Sin plan"
        ciclo = self.get_ciclo_facturacion_display()
        return f"Instalación #{self.pk:05d} - {self.cliente.nombre} {self.cliente.apellido} | {plan_nombre} ({ciclo})"
