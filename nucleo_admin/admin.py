from django_tenants.admin import TenantAdminMixin
from django_tenants.utils import schema_context
from .models import EmpresaISP, Dominio, Paquete
from unfold.admin import ModelAdmin
from django.contrib import admin
import string
import random
import uuid


@admin.register(EmpresaISP)
class EmpresaISPAdmin(TenantAdminMixin, ModelAdmin):
    list_display = (
        "name",
        "schema_name",
        "estado_cuenta",
        "paquete",
        "fecha_proximo_pago",
    )
    search_fields = ("name", "schema_name", "slug")
    list_filter = ("estado_cuenta", "paquete")

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None

        super().save_model(request, obj, form, change)

        if is_new:
            base_domain = 'localhost'
            if not obj.slug:
                obj.slug = f"isp_{uuid.uuid4().hex[:6]}"
                obj.save(update_fields=['slug'])

            domain_str = f"{obj.slug}.{base_domain}"
            Dominio.objects.create(
                domain=domain_str,
                tenant=obj,
                is_primary=True
            )

            if obj.admin_email:
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

                with schema_context(obj.schema_name):
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    if not User.objects.filter(email=obj.admin_email).exists():
                        User.objects.create_superuser(
                            username=obj.admin_email,
                            email=obj.admin_email,
                            password=password
                        )
                        
                        from nucleo_admin.tasks import enviar_correo_bienvenida_isp
                        protocol = request.scheme if request else 'http'
                        url_panel = f"{protocol}://{domain_str}"
                        
                        enviar_correo_bienvenida_isp.delay(
                            email_destino=obj.admin_email,
                            nombre_empresa=obj.name,
                            url_panel=url_panel,
                            password_temporal=password
                        )
                        
                        from django.contrib import messages
                        messages.success(request, f"Empresa creada exitosamente. Las credenciales de acceso han sido enviadas al correo: {obj.admin_email}")

@admin.register(Dominio)
class DominioAdmin(ModelAdmin):
    list_display = (
        "domain",
        "tenant",
        "is_primary"
    )
    search_fields = (
        "domain",
        "tenant__name"
    )
    list_filter = ("is_primary",)


@admin.register(Paquete)
class PaqueteAdmin(ModelAdmin):
    list_display = (
        "nombre",
        "limite_cliente",
        "precio",
        "limite_routers_incluidos",
        "precio_router_extra",
    )
    search_fields = ("nombre",)
