from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from instalaciones.models import Instalacion
from clientes.models import Cliente
from base.admin import admin_site


class InstalacionStackedInline(StackedInline):
    model = Instalacion
    verbose_name_plural = "Gestiona instalaciones"
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    actions = None
    ordering = ("vereda","nombre",)
    list_display = (
        "cliente",
        "vereda_cliente",
        "telefono_cliente",
    )
    inlines = [InstalacionStackedInline,]
    search_fields = (
        "nombre",
        "apellido",
        "vereda"
    )

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f"{obj.nombre} {obj.apellido}"

    @admin.display(description="vereda")
    def vereda_cliente(self, obj):
        return f"{obj.vereda}"

    @admin.display(description="telefono")
    def telefono_cliente(self, obj):
        return f"{obj.telefono}"


admin_site.register(Cliente, ClienteAdmin)
