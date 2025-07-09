from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin


class AdminPersonalizado(AdminSite):
    site_header = "ADMINISTRACIÓN ARINT CONEXIONES"
    index_title = None
    site_title = "ISP Admin"

    def get_app_list(self, request, app_label=None):
        app_dict = self._build_app_dict(request)
        orden = [
            'gestiona facturas y pagos',
            'gestiona clientes',
            'gestiona instalaciones',
            'gestiona planes',
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
