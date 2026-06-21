from django.db.models.aggregates import Sum
from facturacion.models import Cargo
from django.db import models


class Cliente(models.Model):
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=20)
    telefono = models.CharField(max_length=10, blank=True)
    vereda = models.CharField(max_length=20, null=True)

    def calcular_deuda_total(self):
        return Cargo.objects.filter(
            cliente=self,
            estado__in=["pendiente", "parcial"]
        ).aggregate(Sum("saldo_pendiente"))["saldo_pendiente__sum"] or 0

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
