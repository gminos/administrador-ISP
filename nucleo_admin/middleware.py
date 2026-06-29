from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

class TenantSuspensionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if hasattr(request, 'tenant'):
            tenant = request.tenant
            if tenant.schema_name != 'public' and tenant.estado_cuenta == 'suspendida':
                return render(request, 'nucleo_admin/suspendido.html', status=403)
