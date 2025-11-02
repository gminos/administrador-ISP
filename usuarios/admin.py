from django.contrib import admin
from instalaciones.models import Intalacion
from .models import Usuario
from base.admin import admin_site


class InstalacionInline(admin.TabularInline):
    model = Intalacion
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    actions = None
    ordering = ("vereda","nombre",)
    list_display = (
        "cliente",
        "vereda_cliente",
        "telefono_cliente",
    )
    inlines = [InstalacionInline,]
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


admin_site.register(Usuario, UsuarioAdmin)
