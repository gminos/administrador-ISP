from django import forms
from django.contrib import admin
from .models import Plan, UsuarioPlan


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
        return queryset


@admin.register(UsuarioPlan)
class UsuarioPlanAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre",
        "apellido",
        "plan",
        "fecha_inico",
        "fecha_cancelacion",
        "estado_servicio",
    )
    search_fields = (
        "estado_servicio",
        "usuario__nombre",
        "usuario__documento",
        "usuario__apellido",
    )
    autocomplete_fields = ["usuario"]
    list_filter = (EstadoServicioFilter,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["fecha_inico"].widget = forms.HiddenInput()
            form.base_fields["usuario"].widget = forms.HiddenInput()
            form.base_fields["plan"].widget = forms.HiddenInput()
        return form

    def plan(self, obj):
        plan = obj.usuario_plan.nombre
        return plan

    def documento(self, obj):
        return obj.usuario.documento

    def nombre(self, obj):
        return obj.usuario.nombre

    def apellido(self, obj):
        return obj.usuario.apellido


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad_megas", "costo")
