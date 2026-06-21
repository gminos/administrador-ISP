from django.db.models.signals import post_delete, post_save
from instalaciones.models import Instalacion
from django.utils import timezone
from django.dispatch import receiver
from django.db import models
from simple_history.models import HistoricalRecords

METODO_CHOICES = [
    ("transferencia", "Transferencia"),
    ("efectivo", "Efectivo"),
    ("no aplica", "No aplica"),
]
ESTADO_CHOICES = [
    ("pagado", "Pagado"),
    ("pendiente", "Pendiente"),
    ("parcial", "Parcial")
]
TIPO_PAGOS_CHOICES = [
    ("mensualidad","Mensualidad"),
    ("reconexion", "Reconexion")
]
TIPO_CARGO_CHOICES = [
    ("mensualidad", "Mensualidad"),
    ("instalacion", "Instalacion"),
    ("reconexion", "Reconexion")
]


class Factura(models.Model):
    instalacion = models.ForeignKey(
        "instalaciones.Instalacion", on_delete=models.CASCADE
    )
    periodo_inicio = models.DateField(null=True, db_index=True)
    periodo_final = models.DateField(null=True)
    fecha_reconexion = models.DateField(null=True)
    notificacion_enviada = models.BooleanField(default=False)

    @property
    def monto_total(self):
        return self.cargo.monto_total if hasattr(self, 'cargo') else 0

    @property
    def estado(self):
        return self.cargo.estado if hasattr(self, 'cargo') else "pendiente"

    @property
    def cliente(self):
        return self.instalacion.cliente

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ['-periodo_inicio']

    def __str__(self):
        return f"Factura #{self.pk} - {self.cliente}"


class Transaccion(models.Model):
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.CASCADE, related_name="transaciones"
    )
    fecha_pago = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=15, choices=METODO_CHOICES, default="no aplica"
    )
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Transaccion"
        verbose_name_plural = "Transacciones"

    def __str__(self):
        monto_formateado = f"{self.monto_total:,.0f}".replace(",", ".")
        fecha_str = self.fecha_pago.strftime("%d/%m/%Y") if self.fecha_pago else "Sin fecha"
        return f"Transacción #{self.pk:05d} - ${monto_formateado} ({fecha_str})"


class Cargo(models.Model):
    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.CASCADE, related_name="cargos"
    )
    instalacion = models.ForeignKey(
        "instalaciones.Instalacion", on_delete=models.CASCADE, related_name="cargos"
    )
    factura_origen = models.OneToOneField(
        "Factura", null=True, blank=True, on_delete=models.CASCADE
    )
    tipo_cargo = models.CharField(
        choices=TIPO_CARGO_CHOICES, max_length=15, default="mensualidad"
    )
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_emision = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10 ,decimal_places=2)
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(choices=ESTADO_CHOICES, max_length=15, default="pendiente")
    history = HistoricalRecords()

    def __str__(self):
        return f"Cargo #{self.pk:05d} - {self.get_tipo_cargo_display()}"

    def save(self, *args, **kwargs):
        if not self.descripcion:
            nombre_cargo = self.get_tipo_cargo_display().lower()
            self.descripcion = f"Cargo {nombre_cargo}"

        if not self.pk and self.saldo_pendiente is None:
            self.saldo_pendiente = self.monto_total

        super().save(*args, **kwargs)


class DetallePago(models.Model):
    transaccion = models.ForeignKey(
        "Transaccion", on_delete=models.CASCADE, related_name="detallepagos"
    )
    cargo = models.ForeignKey(
        "Cargo", on_delete=models.CASCADE, related_name="detallepagos"
    )
    monto_abonado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto pagado")
    saldo_previo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Deuda inicial")
    saldo_restante = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Deuda final")
    history = HistoricalRecords()

    def __str__(self):
        return f"Detalle de Transacción #{self.transaccion.pk:05d}"


@receiver(post_save, sender=Instalacion)
def crear_cargo_por_instalacion(sender, instance, created, **kwargs):
    if created:
        Cargo.objects.create(
            cliente=instance.cliente,
            instalacion=instance,
            tipo_cargo="instalacion",
            fecha_emision=instance.fecha_instalacion,
            monto_total=instance.costo
        )

@receiver(post_save, sender=Factura)
def crear_cargo_por_factura(sender, instance, created, **kwargs):
    if created:
        costo = instance.instalacion.plan.costo if instance.instalacion.plan else 0
        Cargo.objects.create(
            cliente=instance.instalacion.cliente,
            instalacion=instance.instalacion,
            factura_origen=instance,
            fecha_vencimiento=instance.fecha_reconexion,
            monto_total=costo
        )

@receiver(post_delete, sender=DetallePago)
def restaurar_saldo_cargo_al_borrar_pago(sender, instance, **kwargs):
    cargo = instance.cargo
    cargo.saldo_pendiente += instance.monto_abonado

    if cargo.saldo_pendiente >= cargo.monto_total:
        cargo.estado = "pendiente"
    elif cargo.saldo_pendiente > 0:
        cargo.estado = "parcial"
    else:
        cargo.estado = "pagado"

    cargo.save(update_fields=["saldo_pendiente", "estado"])
