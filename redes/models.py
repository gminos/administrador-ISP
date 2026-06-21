from django.db import models

class Router(models.Model):
    nombre_identificador = models.CharField(max_length=100, help_text="Ej: Nodo Principal, Torre Norte")
    ip = models.GenericIPAddressField(protocol='IPv4', help_text="Dirección IP del equipo Mikrotik")
    puerto_api = models.IntegerField(default=8728, help_text="Por defecto es 8728 (o 8729 si usa SSL)")
    usuario = models.CharField(max_length=50)
    password = models.CharField(max_length=100, verbose_name="Contraseña")
    activo = models.BooleanField(default=True, help_text="Desmarcar si el router está fuera de servicio")

    class Meta:
        verbose_name = "Router"
        verbose_name_plural = "Routers"

    def __str__(self):
        return f"{self.nombre_identificador} ({self.ip})"
