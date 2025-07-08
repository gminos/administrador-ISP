# from django import forms
from django.contrib import admin
from .models import Plan
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


# @admin.register(UsuarioPlan)
# class UsuarioPlanAdmin(admin.ModelAdmin):
#     actions = None
#     list_display = (
#         "nombre",
#         "apellido",
#         "plan",
#         "fecha_inico",
#         "fecha_cancelacion",
#         "estado_servicio",
#     )
#     search_fields = (
#         "estado_servicio",
#         "usuario__nombre",
#         "usuario__apellido",
#     )
#     autocomplete_fields = ["usuario"]
#     list_filter = (EstadoServicioFilter,)
#
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj:
#             # form.base_fields["fecha_inico"].widget = forms.HiddenInput()
#             form.base_fields["usuario"].widget = forms.HiddenInput()
#             form.base_fields["plan"].widget = forms.HiddenInput()
#         return form
#
#     def plan(self, obj):
#         return obj.plan.nombre
#
#     def nombre(self, obj):
#         return obj.usuario.nombre
#
#     def apellido(self, obj):
#         return obj.usuario.apellido


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    actions = None
    list_display = ("nombre", "cantidad_megas", "monto_formateado")

    def monto_formateado(self, obj):
        return f"{obj.costo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    monto_formateado.short_description = 'Valor'


admin_site.register(Plan, PlanAdmin)
# admin_site.register(UsuarioPlan, UsuarioPlanAdmin)
