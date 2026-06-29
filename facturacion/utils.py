from facturacion.models import Factura, Cargo, MetodoPago
from django.template.loader import render_to_string
from django.db import connection
import weasyprint

def generar_pdf_factura(factura: Factura) -> bytes:
    if hasattr(factura, 'cargo'):
        cargos_vencidos = list(Cargo.objects.filter(
            instalacion=factura.instalacion,
            estado__in=['pendiente', 'parcial']
        ).exclude(pk=factura.cargo.pk).order_by("fecha_emision", "pk"))

        saldos_anteriores = sum(c.saldo_pendiente for c in cargos_vencidos)
        saldo_pendiente = factura.cargo.saldo_pendiente
        monto_total = factura.cargo.monto_total
        pagos = factura.cargo.detallepagos.all()
        total_pagado = sum(p.monto_abonado for p in pagos)
    else:
        cargos_vencidos = []
        saldos_anteriores = 0
        saldo_pendiente = 0
        monto_total = 0
        pagos = []
        total_pagado = 0

    total_a_pagar = saldos_anteriores + saldo_pendiente

    tenant = connection.tenant
    metodos_pago = MetodoPago.objects.filter(activo=True)

    html_string = render_to_string('facturacion/factura_pdf.html', {
        'factura': factura, 
        'cargos_vencidos': cargos_vencidos,
        'saldos_anteriores': saldos_anteriores, 
        'total_a_pagar': total_a_pagar,
        'saldo_pendiente': saldo_pendiente,
        'monto_total': monto_total,
        'pagos': pagos,
        'total_pagado': total_pagado,
        'metodos_pago': metodos_pago,
        'tenant': tenant,
    })

    html = weasyprint.HTML(string=html_string)
    return html.write_pdf()
