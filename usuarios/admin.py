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
    list_display = (
        "cliente",
        "vereda",
        "telefono",
    )
    inlines = [
        InstalacionInline,
    ]
    search_fields = (
        "nombre",
        "apellido",
        "vereda"
    )

    def cliente(self, obj):
        return f"{obj.nombre} {obj.apellido}"


admin_site.register(Usuario, UsuarioAdmin)
