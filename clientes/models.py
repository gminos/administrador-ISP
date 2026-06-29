from django.core.exceptions import ValidationError
from django.db.models.aggregates import Sum
from django.db import models, connection
from facturacion.models import Cargo


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

    def clean(self) -> None:
        super().clean()

        if not self.pk:
            tenant = connection.tenant
            if hasattr(tenant, 'schema_name') and tenant.schema_name != 'public':
                if tenant.paquete:
                    limite = tenant.paquete.limite_cliente
                    if limite > 0:
                        cantidad_cliente = Cliente.objects.count()
                        if cantidad_cliente >= limite:
                            raise ValidationError("Has alcanzado el límite máximo de clientes permitidos en tu paquete actual."
                                                  " Por favor, contacta a soporte para mejorar tu plan.")

    class Meta:
        verbose_name = "cliente"
        verbose_name_plural = "clientes"
