from django.contrib import admin
from planes.models import UsuarioPlan
from instalaciones.models import Intalacion
from .models import Usuario
from base.admin import admin_site


class InstalacionInline(admin.TabularInline):
    model = Intalacion
    extra = 0


class UsuarioPlanInline(admin.TabularInline):
    model = UsuarioPlan
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    actions = None
    list_display = (
        "nombre",
        "apellido",
        "vereda",
        "telefono",
    )
    inlines = [
        InstalacionInline,
        UsuarioPlanInline,
    ]
    search_fields = (
        "nombre",
        "apellido",
        "vereda"
    )


admin_site.register(Usuario, UsuarioAdmin)
