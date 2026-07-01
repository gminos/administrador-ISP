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
    ciclo_facturacion = models.IntegerField(choices=CicloFacturacionChoices, default=CicloFacturacionChoices.MENSUAL)
    router = models.ForeignKey("redes.Router", on_delete=models.PROTECT)
    pppoe_usuario = models.CharField(max_length=50, unique=True, null=True, blank=True)
    pppoe_password = models.CharField(max_length=100, null=True, blank=True)
    ip_estatica = models.GenericIPAddressField("IP Estática", null=True, blank=True, help_text="Opcional. Dejar en blanco para IP Dinámica.")

    class Meta:
        verbose_name = "instalacion"
        verbose_name_plural = "instalaciones"

    def __str__(self):
        plan_nombre = self.plan.nombre if self.plan else "Sin plan"
        ciclo = self.get_ciclo_facturacion_display()
        pk_str = f"{self.pk:05d}" if self.pk else "Sin ID"
        return f"Instalación #{pk_str} - {self.cliente.nombre} {self.cliente.apellido} | {plan_nombre} ({ciclo})"

    def clean(self):
        super().clean()
        if self.pppoe_usuario == "":
            self.pppoe_usuario = None
