from django.db import models
from django.core.exceptions import ValidationError


class Plan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)
    cantidad_megas = models.IntegerField(help_text="Velocidad del plan en Mbps")
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "plan"
        verbose_name_plural = "planes"

    def __str__(self):
        return f"{self.nombre}"


class UsuarioPlan(models.Model):
    usuario_plan_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", on_delete=models.CASCADE, related_name="usuario_plan"
    )
    plan = models.ForeignKey(
        "Plan", on_delete=models.CASCADE, related_name="usuario_plan"
    )
    fecha_inico = models.DateTimeField()
    fecha_cancelacion = models.DateTimeField(blank=True, null=True)
    estado_servicio = models.BooleanField(default=True)

    class Meta:
        verbose_name = "plan-usuario"
        verbose_name_plural = "planes-usuarios"

    def __str__(self):
        return f"Informacion de {self.usuario.nombre} {self.usuario.apellido}"

    def clean(self):
        if self.estado_servicio and self.fecha_cancelacion is not None:
            raise ValidationError(
                "Si el servicio esta activo, no debe tener fecha de cancelacion"
            )
        if not self.estado_servicio and self.fecha_cancelacion is None:
            raise ValidationError(
                "Si el servicio esta cancelado, debe tener una fecha de cancelacion"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
