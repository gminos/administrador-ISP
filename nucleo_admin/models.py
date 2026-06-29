from django_tenants.models import TenantMixin, DomainMixin
from django.core.exceptions import ValidationError
from django.db import connection
from django.db import models


ESTADO_CUENTA_CHOICES = [
    ('activa', 'Activa'),
    ('mora', 'En Mora'),
    ('suspendida', 'Suspendida')
]

class EmpresaISP(TenantMixin):
    name = models.CharField("Nombre de la empresa", max_length=100)
    slug = models.SlugField("URL (Slug)", max_length=100, unique=True, blank=True)
    admin_email = models.EmailField("Email del Dueño", max_length=254, blank=True, null=True)
    logo = models.ImageField("Logo de la empresa", upload_to="logos_inquilinos/", null=True, blank=True)
    wa_token = models.CharField("Token de WhatsApp", max_length=500, blank=True, null=True)
    wa_phone_id = models.CharField("ID de Teléfono WhatsApp", max_length=100, blank=True, null=True)
    auto_create_schema = True
    paquete = models.ForeignKey("Paquete", on_delete=models.SET_NULL, related_name="empresas", null=True, blank=True)
    routers_extras_contratados = models.IntegerField(default=0)
    estado_cuenta = models.CharField(max_length=20, choices=ESTADO_CUENTA_CHOICES, default='activa')
    fecha_proximo_pago = models.DateField(null=True, blank=True)
    dias_gracia = models.IntegerField(default=3)

    class Meta:
        verbose_name = "Empresa ISP"
        verbose_name_plural = "Empresas ISP"

    def clean(self):
        super().clean()

        if not self.pk and self.schema_name:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
                    [self.schema_name]
                )
                if cursor.fetchone():
                    raise ValidationError({'schema_name': 'Ya existe un esquema físico en la base de datos con este nombre. Por favor, elige otro o contacta a soporte para limpiarlo.'})

    def __str__(self):
        return self.name

class Dominio(DomainMixin):
    class Meta:
        verbose_name = "Dominio"
        verbose_name_plural = "Dominios"


class Paquete(models.Model):
    nombre = models.CharField(max_length=50)
    limite_cliente = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    limite_routers_incluidos = models.IntegerField(default=2, help_text="Routers base del paquete")
    precio_router_extra = models.DecimalField(max_digits=10, decimal_places=2, default=25000.00)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Paquete"
        verbose_name_plural = "Paquetes"
