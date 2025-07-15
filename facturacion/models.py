from django.db import models

MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

METODO_CHOICES = [("transferencia", "Transferencia"),
                  ("efectivo", "Efectivo"), ("no aplica", "No aplica")]
ESTADO_CHOICES = [("pagado", "Pagado"),
                  ("pendiente", "Pendiente"), ("se acumula", "Se acumula")]
TIPO_PAGOS_CHOICES = [("mensualidad", "Mensualidad"),
                      ("reconexion", "Reconexion")]


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="factura"
    )
    codigo_factura = models.CharField(null=True)
    periodo_inicio = models.DateField(null=True)
    periodo_final = models.DateField(null=True)
    fecha_reconexion = models.DateField(null=True)
    monto_a_pagar = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        dia_inicio = self.periodo_inicio.day
        dia_final = self.periodo_final.day
        mes = MESES[self.periodo_final.month].capitalize()
        return f"Periodo facturado: {dia_inicio} ~ {dia_final} {mes}"

    class Meta:
        verbose_name = "factura"
        verbose_name_plural = "Administra facturas y pagos"


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
    fecha_pago = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ''
