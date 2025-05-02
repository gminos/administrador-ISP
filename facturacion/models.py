from django.db import models


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="usuario"
    )
    fecha_emision = models.DateTimeField(blank=True, null=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
