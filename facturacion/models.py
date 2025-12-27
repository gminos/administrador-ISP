from django.db import models
from django.core.exceptions import ValidationError
from django.utils.formats import date_format

METODO_CHOICES = [("transferencia", "Transferencia"),
                  ("efectivo", "Efectivo"), ("no aplica", "No aplica")]
ESTADO_CHOICES = [("pagado", "Pagado"),
                  ("pendiente", "Pendiente")]
TIPO_PAGOS_CHOICES = [("mensualidad", "Mensualidad"),
                      ("reconexion", "Reconexion")]


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.CASCADE, related_name="factura"
    )
    periodo_inicio = models.DateField(null=True, db_index=True)
    periodo_final = models.DateField(null=True)
    fecha_reconexion = models.DateField(null=True)

    def __str__(self):
        if not self.periodo_final:
            return f"Factura {self.factura_id}"
        dia_inicio = self.periodo_inicio.day
        dia_final = self.periodo_final.day
        mes = date_format(self.periodo_final, "F").capitalize()
        return f"Periodo facturado: {dia_inicio} ~ {dia_final} {mes}"

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"


class Pago(models.Model):
    pago_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="pagos", null=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_pago = models.CharField(
        max_length=15, choices=TIPO_PAGOS_CHOICES, default="mensualidad", null=True)
    metodo_pago = models.CharField(
        max_length=15, choices=METODO_CHOICES, default="no aplica")
    estado = models.CharField(
        max_length=10, choices=ESTADO_CHOICES, default="pendiente"
    )
    fecha_pago = models.DateField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.estado == "pagado" and self.fecha_pago is None:
            raise ValidationError({
                "fecha_pago": "Debe proporcionar una fecha de pago si el estado es 'pagado'."
            })

        if self.estado == "pagado" and self.metodo_pago == "no aplica":
            raise ValidationError({
                "metodo_pago": "No puedes dejar este metodo de pago."
            })

        if self.estado == "pendiente" and self.fecha_pago is not None:
            raise ValidationError({
                "fecha_pago": "No puede existir una fecha pago si el estado es 'pendiente'."
            })

    def __str__(self):
        return ''
