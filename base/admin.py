from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin


class AdminPersonalizado(AdminSite):
    site_header = "Administración de Arint Conexiones"
    index_title = "Panel de Administración"
    site_title = "ISP Admin"

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        orden = [
            'facturación',
            'gestiona clientes y direcciones',
            'gestiona instalaciones',
            'Crea planes / asigna a clientes',
            'Autenticación y autorización',
        ]
        return sorted(
            app_dict.values(),
            key=lambda x: orden.index(
                x['name']) if x['name'] in orden else len(orden)
        )


admin_site = AdminPersonalizado(name='miadmin')

admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
