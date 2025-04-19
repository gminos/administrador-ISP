from django.contrib import admin
from .models import Intalacion


@admin.register(Intalacion)
class InstalacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "fecha_instalacion", "costo")
    search_fields = ("usuario__documento",
                     "usuario__nombre", "usuario__apellido")
    autocomplete_fields = ["usuario"]
