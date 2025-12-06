from django.db import models


class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    cantidad_megas = models.IntegerField(
        help_text="Velocidad del plan en Mbps")
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "plan"
        verbose_name_plural = "planes"

    def __str__(self):
        return f"{self.nombre}"
