from django.db import models

MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="usuario"
    )
    codigo = models.IntegerField(null=True)
    periodo_inicio = models.DateField(null=True)
    periodo_final = models.DateField(null=True)
    monto_a_pagar = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        inicio = MESES[self.periodo_inicio.month]
        final = MESES[self.periodo_final.month]
        return f"{self.usuario} :: {inicio.upper()} hasta {final.upper()}"

    class Meta:
        verbose_name = "factura"
        verbose_name_plural = "Administra facturas y pagos"


class DetalleFactura(models.Model):
    TIPO_DETALLE_CHOICES = [
        ("mensualidad", "Mensualidad"),
        ("instalación", "Instalación"),
        ("reconexión", "Reconexión"),
    ]
    detalle_factura_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="detalles"
    )
    tipo_detalle = models.CharField(
        max_length=20, choices=TIPO_DETALLE_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)


class Pago(models.Model):
    METODO_CHOICES = [("transferencia", "Transferencia"),
                      ("efectivo", "Efectivo")]
    ESTADO_CHOICES = [("pagado", "Pagado"), ("pendiente", "Pendiente")]
    pago_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="pagos", null=True
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=15, choices=METODO_CHOICES)
    estado = models.CharField(
        max_length=10, choices=ESTADO_CHOICES, default="pendiente"
    )
    fecha_pago = models.DateTimeField(auto_now_add=True)
