from django.contrib import admin
from unfold.admin import ModelAdmin
from planes.models import Plan
from base.admin import admin_site


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
            return queryset.filter(estado_servicio=True)
        if self.value() == "inactivo":
            return queryset.filter(estado_servicio=False)


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    actions = None
    list_display = ("nombre", "cantidad_megas", "monto_formateado")

    def monto_formateado(self, obj):
        return f"{obj.costo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_formateado.short_description = 'Valor'


admin_site.register(Plan, PlanAdmin)