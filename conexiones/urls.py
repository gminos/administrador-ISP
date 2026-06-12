from django.urls import path
from base.admin import admin_site
from facturacion import views as facturacion_views

urlpatterns = [
    path('facturacion/transaccion/<int:trx_id>/recibo/', facturacion_views.descargar_recibo_transaccion, name='descargar_recibo_transaccion'),
    path('caja/', facturacion_views.portal_caja_view, name='portal_caja'),
    path('', admin_site.urls),
]
