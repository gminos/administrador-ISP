from django.urls import path
from base.admin import admin_site
from facturacion.views import descargar_comprobante_pdf_view

urlpatterns = [
    path('comprobante/<int:pago_id>/', descargar_comprobante_pdf_view, name='descargar_comprobante'),
    path("", admin_site.urls),
]
