from django.db import models

METODO_CHOICES = [("transferencia", "Transferencia"),
                  ("efectivo", "Efectivo"), ("no aplica", "No aplica")]
ESTADO_CHOICES = [("pagado", "Pagado"),
                  ("pendiente", "Pendiente")]
TIPO_PAGOS_CHOICES = [("mensualidad", "Mensualidad"),
                      ("reconexion", "Reconexion")]


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

    class Meta:
        verbose_name = "factura"
        verbose_name_plural = "facturas"

    def __str__(self):
        return f"Factura #{self.pk} - {self.cliente}"


class Pago(models.Model):
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="pagos", null=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(
        max_length=15, choices=TIPO_PAGOS_CHOICES, default="mensualidad", null=True)
    metodo_pago = models.CharField(
        max_length=15, choices=METODO_CHOICES, default="no aplica")
    fecha_pago = models.DateField(null=True, blank=True)

    def __str__(self):
        factura_id = self.factura.pk if self.factura else "N/A"
        return f"Abono de ${self.monto_pagado} (Factura #{factura_id})"
