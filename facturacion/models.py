from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

METODO_CHOICES = [("transferencia", "Transferencia"), ("efectivo", "Efectivo"), ("no aplica", "No aplica")]
ESTADO_CHOICES = [("pagado", "Pagado"), ("pendiente", "Pendiente"), ("parcial", "Parcial")]
TIPO_PAGOS_CHOICES = [("mensualidad", "Mensualidad"), ("reconexion", "Reconexion")]


class Factura(models.Model):
    instalacion = models.ForeignKey(
        "instalaciones.Instalacion", on_delete=models.CASCADE
    )
    periodo_inicio = models.DateField(null=True, db_index=True)
    periodo_final = models.DateField(null=True)
    fecha_reconexion = models.DateField(null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="pendiente")

    @property
    def cliente(self):
        return self.instalacion.cliente

    @property
    def total_pagado(self):
        return sum(pago.monto_pagado for pago in self.pagos.all())

    @property
    def saldo_pendiente(self):
        return self.monto_total - self.total_pagado

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-periodo_inicio']

    def __str__(self):
        return f"Factura #{self.pk} - {self.cliente}"


class Pago(models.Model):
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="pagos", null=True
    )
    transaccion = models.ForeignKey(
        "Transaccion", on_delete=models.CASCADE, related_name="pagos"
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(
        max_length=15, choices=TIPO_PAGOS_CHOICES, default="mensualidad", null=True
    )

    def __str__(self):
        factura_id = self.factura.pk if self.factura else "N/A"
        return f"Abono de ${self.monto_pagado} (Factura #{factura_id})"


class Transaccion(models.Model):
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.CASCADE, related_name="transaciones"
    )
    fecha_pago = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=15, choices=METODO_CHOICES, default="no aplica"
    )

    def __str__(self):
        return f"Trx #{self.pk} - ${self.monto_total} ({self.fecha_pago})"

@receiver([post_save, post_delete], sender=Pago)
def actualizar_estado_factura(sender, instance, **kwargs):
    try:
        factura = Factura.objects.get(pk=instance.factura.pk)
    except Factura.DoesNotExist:
        return

    saldo_pendiente = factura.saldo_pendiente

    if saldo_pendiente <= 0:
        factura.estado = "pagado"
    elif saldo_pendiente < factura.monto_total:
        factura.estado = "parcial"
    else:
        factura.estado = "pendiente"

    factura.save()
