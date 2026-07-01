from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.db import models

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


class MetodoPago(models.Model):
    nombre = models.CharField("Metodo de pago", max_length=100)
    detalles = models.TextField("Detalles de la cuenta", help_text="Ej: Número 3001234567 a nombre de Juan")
    activo = models.BooleanField("Activo", default=True)

    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre}"


class ConfiguracionFacturacion(models.Model):
    dias_gracia = models.PositiveIntegerField(
        "Días de gracia",
        default=3,
        help_text="Días adicionales después del corte del ciclo antes de cobrar reconexión"
    )

    class Meta:
        verbose_name = "Regla de Reconexión"
        verbose_name_plural = "Regla de Reconexión"

    def save(self, *args, **kwargs):
        if not self.pk and ConfiguracionFacturacion.objects.exists():
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuración Global"


class Factura(models.Model):
    instalacion = models.ForeignKey(
        "instalaciones.Instalacion", on_delete=models.PROTECT
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
        "clientes.Cliente", on_delete=models.PROTECT, related_name="transaciones"
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
        "clientes.Cliente", on_delete=models.PROTECT, related_name="cargos"
    )
    instalacion = models.ForeignKey(
        "instalaciones.Instalacion", on_delete=models.PROTECT, related_name="cargos"
    )
    factura_origen = models.OneToOneField(
        "Factura", null=True, blank=True, on_delete=models.SET_NULL
    )
    tipo_cargo = models.CharField(
        choices=TIPO_CARGO_CHOICES, max_length=15, default="mensualidad"
    )
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_emision = models.DateField(default=timezone.localdate)
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

        if self.monto_total == 0 and self.estado != "pagado":
            self.estado = "pagado"
            self.saldo_pendiente = 0

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