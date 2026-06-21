from unfold.contrib.filters.admin import RadioFilter
from unfold.admin import ModelAdmin, StackedInline
from django.core.validators import EMPTY_VALUES
from instalaciones.models import Instalacion
from clientes.models import Cliente
from django.contrib import admin

class InstalacionStackedInline(StackedInline):
    model = Instalacion
    verbose_name_plural = "Gestiona instalaciones"
    extra = 0


class EstadoServicioFilter(RadioFilter):
    title = "estado del servicio"
    parameter_name = "estado_servicio"

    def lookups(self, request, model_admin):
        return (
            ("activos", "Activos"),
            ("inactivos", "Inactivos"),
        )

    def queryset(self, request, queryset):
        if self.value() == "activos":
            return queryset.filter(instalaciones__servicio_activo=True).distinct()
        if self.value() == "inactivos":
            return queryset.exclude(instalaciones__servicio_activo=True)
        return queryset


class VeredaClienteFilter(RadioFilter):
    title = "vereda"
    parameter_name = "vereda"

    def lookups(self, request, model_admin):
        veredas_crudas = Cliente.objects.values_list('vereda', flat=True)
        veredas_limpias = set(v.strip().lower() for v in veredas_crudas if v and v.strip())
        return [(v, v.title()) for v in sorted(veredas_limpias)]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            if self.value():
                return queryset.filter(vereda__iexact=self.value())
        return queryset


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    actions = None
    sortable_by = ()
    ordering = (
        "vereda",
        "nombre",
    )
    list_display = (
        "cliente",
        "vereda",
        "telefono",
    )
    list_filter = (
        EstadoServicioFilter,
        VeredaClienteFilter,
    )
    list_filter_submit = True
    show_facets = admin.ShowFacets.NEVER
    inlines = [InstalacionStackedInline,]
    search_fields = (
        "nombre",
        "apellido",
        "vereda",
        "telefono"
    )

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f"{obj.nombre} {obj.apellido}"
