from django.core.exceptions import ValidationError
from django.db import connection
from django.db import models

class Router(models.Model):
    nombre_identificador = models.CharField(max_length=100, help_text="Ej: Nodo Principal, Torre Norte")
    ip = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="Opcional si usas VPN")
    ip_vpn = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="Dirección IP asignada por la VPN")
    wg_client_id = models.CharField(max_length=100, null=True, blank=True, help_text="ID interno en el servidor WireGuard")
    puerto_api = models.IntegerField(default=8728, help_text="Por defecto es 8728 (o 8729 si usa SSL)")
    usuario = models.CharField(max_length=50)
    password = models.CharField(max_length=100, verbose_name="Contraseña")
    activo = models.BooleanField(default=True, help_text="Desmarcar si el router está fuera de servicio")

    class Meta:
        verbose_name = "Router"
        verbose_name_plural = "Routers"

    def clean(self):
        super().clean()
        if not self.pk:
            tenant = connection.tenant
            if hasattr(tenant, 'paquete') and tenant.paquete:
                limite_total = tenant.paquete.limite_routers_incluidos + tenant.routers_extras_contratados
                routers_actuales = Router.objects.count()
                if routers_actuales >= limite_total:
                    raise ValidationError(f"Has alcanzado el límite de {limite_total} routers de tu plan. Adquiere adicionales en tu suscripción.")

    def __str__(self):
        return f"{self.nombre_identificador} ({self.ip_vpn or self.ip})"
