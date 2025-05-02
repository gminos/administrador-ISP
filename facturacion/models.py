from django.db import models


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="usuario"
    )
    fecha_emision = models.DateTimeField(blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)


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
    ESTADO_CHOICES = [("cancelado", "Cancelado"), ("pendiente", "Pendiente")]
    pago_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        "Factura", on_delete=models.CASCADE, related_name="pagos"
    )
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=15, choices=METODO_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES)
    fecha_pago = models.DateTimeField(auto_now_add=True)
