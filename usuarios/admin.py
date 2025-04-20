from django.contrib import admin
from planes.models import UsuarioPlan
from instalaciones.models import Intalacion
from .models import Usuario, Direccion


class InstalacionInline(admin.TabularInline):
    model = Intalacion
    extra = 0


class UsuarioPlanInline(admin.TabularInline):
    model = UsuarioPlan
    extra = 0


# Crear direcciones al momento de crear un usuario
class DireccionInline(admin.TabularInline):
    model = Direccion
    extra = 0


class EstadoServicioFilter(admin.SimpleListFilter):
    title = "Estado del servicio"
    parameter_name = "estado_servicio"

    def lookups(self, request, model_admin):
        return (
            ("activo", "Activo"),
            ("inactivo", "Inactivo"),
        )

    def queryset(self, request, queryset):
        if self.value() == "activo":
            return queryset.filter(usuario_plan__estado_servicio=True)
        if self.value() == "inactivo":
            return queryset.filter(usuario_plan__estado_servicio=False)
        return queryset


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre",
        "apellido",
        "telefono",
        "plan",
        "estado_servicio",
        "direccion",
        "instalacion",
        "cancelacion",
    )
    inlines = [DireccionInline, UsuarioPlanInline, InstalacionInline]
    search_fields = (
        "documento",
        "nombre",
        "apellido",
        "direcciones__vereda",
        "usuario_plan__plan__nombre",
    )
    list_filter = (EstadoServicioFilter,)

    # No editar documento pero si al momento de crear
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("documento",)
        return ()

    def plan(self, obj):
        planes = obj.usuario_plan.filter(estado_servicio=True)
        if planes.exists():
            return ", ".join(str(p.plan) for p in planes)
        return "Sin ningun plan"

    def direccion(self, obj):
        direcciones = obj.direcciones.all()
        if direcciones.exists():
            return ", ".join(d.vereda for d in direcciones)
        return "Sin dirección"

    def instalacion(self, obj):
        instalaciones = obj.instalacion.all()
        if instalaciones.exists():
            return ", ".join(
                i.fecha_instalacion.strftime("%Y-%m-%d") for i in instalaciones
            )
        return "Sin instalaciones"

    def estado_servicio(self, obj):
        estados = obj.usuario_plan.values_list(
            "estado_servicio", flat=True).distinct()

        etiquetas = []

        for estado in estados:
            if estado:
                etiquetas.append("Activo")
            else:
                etiquetas.append("Inactivo")

        return ", ".join(etiquetas) if etiquetas else "Sin servicio"

    def cancelacion(self, obj):
        cancelaciones = obj.usuario_plan.filter(estado_servicio=False)
        if cancelaciones.exists():
            return ", ".join(
                c.fecha_cancelacion.strftime("%Y-%m-%d") for c in cancelaciones
            )
        return "Sin cancelaciones"


@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre",
        "apellido",
        "vereda",
        "descripcion",
    )
    search_fields = (
        "vereda",
        "usuario__documento",
        "usuario__nombre",
        "usuario__apellido",
    )
    autocomplete_fields = ["usuario"]

    def nombre(self, obj):
        return obj.usuario.nombre

    def apellido(self, obj):
        return obj.usuario.apellido

    def documento(self, obj):
        return obj.usuario.documento
