from redes.mikrotik_cliente import suspender_cliente, reactivar_cliente, consultar_estado_cliente
from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from .models import Instalacion

@admin.register(Instalacion)
class InstalacionAdmin(ModelAdmin):
    actions = [
        "action_suspender",
        "action_reactivar",
        "action_consultar_estado"
    ]
    list_display = (
        "cliente",
        "vereda",
        "pppoe_usuario",
        "ip_estatica",
        "fecha_instalacion",
        "costo",
        "servicio_activo"
    )
    search_fields = (
        "cliente__nombre",
        "cliente__apellido",
        "pppoe_usuario",
        "ip_estatica"
    )
    autocomplete_fields = ["cliente"]
    readonly_fields = ["cliente"]

    @admin.action(description="Mikrotik: Suspender cliente/s")
    def action_suspender(self, request, queryset):
        exitosos = 0
        for instalacion in queryset:
            if not instalacion.router or not instalacion.pppoe_usuario:
                self.message_user(request, f"Omitido: {instalacion.cliente} no tiene router o usuario PPPoE asignado.", messages.WARNING)
                continue

            exito, mensaje = suspender_cliente(instalacion.router, instalacion.pppoe_usuario)

            if exito:
                instalacion.servicio_activo = False
                instalacion.save()
                exitosos += 1
            else:
                self.message_user(request, f"Fallo al suspender a {instalacion.pppoe_usuario}: {mensaje}", messages.ERROR)

        if exitosos > 0:
            self.message_user(request, f"Se suspendieron {exitosos} cliente/s exitosamente.", messages.SUCCESS)

    @admin.action(description="Mikrotik: Reactivar cliente/s")
    def action_reactivar(self, request, queryset):
        exitosos = 0
        for instalacion in queryset:
            if not instalacion.router or not instalacion.pppoe_usuario:
                self.message_user(request, f"Omitido: {instalacion.cliente} no tiene router o usuario PPPoE asignado.", messages.WARNING)
                continue

            exito, mensaje = reactivar_cliente(instalacion.router, instalacion.pppoe_usuario)

            if exito:
                instalacion.servicio_activo = True
                instalacion.save()
                exitosos += 1
            else:
                self.message_user(request, f"Fallo al reactivar a {instalacion.pppoe_usuario}: {mensaje}", messages.ERROR)

        if exitosos > 0:
            self.message_user(request, f"Se reactivaron {exitosos} clientes en Mikrotik exitosamente.", messages.SUCCESS)

    @admin.action(description="Mikrotik: Consultar estado de conexión")
    def action_consultar_estado(self, request, queryset):
        for instalacion in queryset:
            if not instalacion.router or not instalacion.pppoe_usuario:
                self.message_user(request, f"Omitido: {instalacion.cliente} no tiene router o usuario PPPoE asignado.", messages.WARNING)
                continue

            exito, esta_conectado, mensaje = consultar_estado_cliente(instalacion.router, instalacion.pppoe_usuario)
            if exito:
                if esta_conectado:
                    self.message_user(request, f"{instalacion.cliente}: {mensaje}", messages.SUCCESS)
                else:
                    self.message_user(request, f"{instalacion.cliente}: {mensaje}", messages.WARNING)
            else:
                self.message_user(request, f"{instalacion.cliente}: {mensaje}", messages.ERROR)

    @admin.display(description="cliente", ordering="cliente__nombre")
    def get_cliente_nombre(self, obj):
        return f"{obj.cliente.nombre} {obj.cliente.apellido}"

    @admin.display(description="Vereda", ordering="cliente__vereda")
    def vereda(self, obj):
        return obj.cliente.vereda
