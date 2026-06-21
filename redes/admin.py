from .mikrotik_cliente import obtener_desconectados
from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from .models import Router

@admin.register(Router)
class RouterAdmin(ModelAdmin):
    actions = ["action_ver_desconectados"]
    list_display = ('nombre_identificador', 'ip', 'puerto_api', 'activo')
    search_fields = ('nombre_identificador', 'ip')
    list_filter = ('activo',)

    @admin.action(description="Mikrotik: Ver usuarios desconectados")
    def action_ver_desconectados(self, request, queryset):
        for router in queryset:
            exito, respuesta = obtener_desconectados(router)
            if exito:
                cantidad = len(respuesta)
                if cantidad > 0:
                    nombres = ", ".join(respuesta)
                    self.message_user(request, f"{router.nombre_identificador}: Hay {cantidad} usuarios desconectados -> {nombres}", messages.WARNING)
                else:
                    self.message_user(request, f"{router.nombre_identificador}: Todos los usuarios habilitados están conectados.", messages.SUCCESS)
            else:
                self.message_user(request, f"Error conectando a {router.nombre_identificador}: {respuesta}", messages.ERROR)



