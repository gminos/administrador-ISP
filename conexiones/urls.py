from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from facturacion import views as facturacion_views

admin.site.site_header = "Arint Conexiones"
admin.site.site_title = "Arint Conexiones"
admin.site.index_title = "Panel de control"

urlpatterns = [
    path('facturacion/transaccion/<int:trx_id>/recibo/', facturacion_views.descargar_recibo_transaccion, name='descargar_recibo_transaccion'),
    path('caja/', facturacion_views.PortalCajaView.as_view(), name='portal_caja'),
    path('', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
