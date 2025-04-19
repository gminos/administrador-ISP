from django.contrib import admin
from planes.models import UsuarioPlan
from .models import Usuario, Direccion


class UsuarioPlanInline(admin.TabularInline):
    model = UsuarioPlan
    extra = 0


# Crear direcciones al momento de crear un usuario
class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 0


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre",
        "apellido",
        "telefono",
        "plan",
        "direccion",
    )
    inlines = [DireccionInline, UsuarioPlanInline]
    search_fields = ("documento", "nombre", "apellido", "direcciones__vereda")

    # No editar documento pero si al momento de crear
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("documento",)
        return ()

    def plan(self, obj):
        planes = obj.usuario_plan.filter(estado_servicio=True)
        if planes.exists():
            return ", ".join(str(p.plan) for p in planes)
        return "Sin plan activo"

    def direccion(self, obj):
        direcciones = obj.direcciones.all()
        if direcciones.exists():
            return ", ".join(d.vereda for d in direcciones)
        return "Sin dirección"


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("vereda", "descripcion", "usuario_documento")
    search_fields = ("vereda", "usuario__documento")

    # Mostrar el documento
    def usuario_documento(self, obj):
        return obj.usuario.documento

    usuario_documento.short_description = "documento"
