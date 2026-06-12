from django.db import models
from django.db.models.aggregates import Sum

from facturacion.models import Factura, Pago


class Cliente(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10, blank=True)
    vereda = models.CharField(max_length=20, null=True)

    def calcular_deuda_total(self):
        monto_facturas = Factura.objects.filter(
            instalacion__cliente=self,
            estado__in=["pendiente", "parcial"]
        ).aggregate(Sum("monto_total"))["monto_total__sum"] or 0

        monto_pagos = Pago.objects.filter(
            factura__instalacion__cliente=self,
            factura__estado__in=["pendiente", "parcial"]
        ).aggregate(Sum("monto_pagado"))["monto_pagado__sum"] or 0

        return monto_facturas - monto_pagos

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
