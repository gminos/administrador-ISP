from django.contrib import admin
from unfold.admin import ModelAdmin
from instalaciones.models import Intalacion
from clientes.models import Cliente
from base.admin import admin_site
from django.db import models
from unfold.widgets import UnfoldAdminSplitDateTimeWidget, UnfoldAdminTextInputWidget, UnfoldAdminSelectWidget


class InstalacionInline(admin.TabularInline):
    model = Intalacion
    extra = 0
    formfield_overrides = {
        models.DateTimeField: {"widget": UnfoldAdminSplitDateTimeWidget},
        models.DecimalField: {"widget": UnfoldAdminTextInputWidget},
    }

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "plan":
            kwargs["widget"] = UnfoldAdminSelectWidget(attrs={"style": "width: 100%;"})
            return db_field.formfield(**kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    actions = None
    ordering = ("vereda","nombre",)
    list_display = (
        "cliente",
        "vereda_cliente",
        "telefono_cliente",
    )
    inlines = [InstalacionInline,]
    search_fields = (
        "nombre",
        "apellido",
        "vereda"
    )

    @admin.display(description="cliente")
    def cliente(self, obj):
        return f"{obj.nombre} {obj.apellido}"

    @admin.display(description="vereda")
    def vereda_cliente(self, obj):
        return f"{obj.vereda}"

    @admin.display(description="telefono")
    def telefono_cliente(self, obj):
        return f"{obj.telefono}"


admin_site.register(Cliente, ClienteAdmin)
