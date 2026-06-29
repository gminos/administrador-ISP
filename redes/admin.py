from .mikrotik_cliente import obtener_desconectados
from django.contrib import admin, messages
from unfold.admin import ModelAdmin
from .models import Router

@admin.register(Router)
class RouterAdmin(ModelAdmin):
    actions = ["action_ver_desconectados", "action_generar_script_vpn"]
    list_display = ('nombre_identificador', 'ip', 'ip_vpn', 'puerto_api', 'activo')
    search_fields = ('nombre_identificador', 'ip', 'ip_vpn')
    list_filter = ('activo',)
    readonly_fields = ('ip_vpn',)
    exclude = ('wg_client_id',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Generar VPN automáticamente si no se proveyó una IP pública ni tiene VPN aún
        if not obj.ip and not obj.wg_client_id:
            from django.utils.text import slugify
            from redes.services.vpn import WireguardManager
            
            try:
                wg = WireguardManager()
                nombre_cliente = f"router_{obj.id}_{slugify(obj.nombre_identificador)[:15]}"
                cliente_data = wg.create_client(nombre_cliente)
                
                if cliente_data:
                    obj.wg_client_id = cliente_data.get('id')
                    obj.ip_vpn = cliente_data.get('address')
                    obj.save(update_fields=['wg_client_id', 'ip_vpn'])
                else:
                    messages.warning(request, "El router se guardó, pero no se pudo generar la VPN automáticamente.")
            except Exception as e:
                messages.warning(request, f"El router se guardó, pero falló la conexión al servidor VPN: {e}")

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

    @admin.action(description="Mikrotik: Generar Script VPN")
    def action_generar_script_vpn(self, request, queryset):
        from django.http import HttpResponse
        from django.utils.text import slugify
        from redes.services.vpn import WireguardManager
        from redes.utils.mikrotik_script import generate_mikrotik_wg_script

        if queryset.count() != 1:
            self.message_user(request, "Por favor seleccione solo UN router para generar su script.", messages.ERROR)
            return

        router = queryset.first()
        try:
            wg = WireguardManager()
            
            if not router.wg_client_id:
                nombre_cliente = f"router_{router.id}_{slugify(router.nombre_identificador)[:15]}"
                cliente_data = wg.create_client(nombre_cliente)
                
                if cliente_data:
                    router.wg_client_id = cliente_data.get('id')
                    router.ip_vpn = cliente_data.get('address')
                    router.save(update_fields=['wg_client_id', 'ip_vpn'])
                else:
                    self.message_user(request, "Error al crear cliente VPN en wg-easy.", messages.ERROR)
                    return
                    
            config_text = wg.get_client_config(router.wg_client_id)
            
            # Usar la IP desde la cual el admin esta accediendo al panel (asumiendo que es la misma que tendra el VPN)
            host_publico = request.get_host().split(':')[0]
            if host_publico in ['localhost', '127.0.0.1']:
                host_publico = "TU_IP_PUBLICA_O_DDNS"
                
            script = generate_mikrotik_wg_script(config_text, host_publico)
            return HttpResponse(script, content_type="text/plain; charset=utf-8")
            
        except Exception as e:
            self.message_user(request, f"Error en el servidor VPN: {e}", messages.ERROR)



