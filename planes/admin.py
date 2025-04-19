from django.contrib import admin
from .models import Plan, UsuarioPlan


@admin.register(UsuarioPlan)
class UsuarioPlanAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "plan",
        "fecha_inico",
        "fecha_cancelacion",
        "estado_servicio",
    )
    search_fields = (
        "estado_servicio",
        "usuario__nombre",
        "usuario__documento",
    )
    autocomplete_fields = ["usuario"]


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cantidad_megas", "costo")
