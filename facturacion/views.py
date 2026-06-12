from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.template.loader import render_to_string
from facturacion.models import Pago, Transaccion, Factura
from clientes.models import Cliente
from base.admin import admin_site
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
import weasyprint

@staff_member_required
def descargar_recibo_transaccion(request, trx_id):
    transaccion = get_object_or_404(Transaccion, pk=trx_id)
    html_string = render_to_string('facturacion/recibo_transaccion_pdf.html', {'transaccion': transaccion})
    html = weasyprint.HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_trx_{transaccion.pk}.pdf"'
    return response


@staff_member_required
def portal_caja_view(request):
    context = admin_site.each_context(request)
    context.update({'title': 'Caja rápida'})

    if request.method == "POST":
        cliente_id = request.POST.get('cliente_id')
        monto_str = request.POST.get('monto')
        metodo = request.POST.get('metodo')

        if not cliente_id or not monto_str:
            messages.error(request, "Faltan datos para procesar el pago.")
            return redirect('portal_caja')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        try:
            monto_recibido = Decimal(monto_str)
        except:
            messages.error(request, "Monto inválido.")
            return redirect('portal_caja')

        if monto_recibido <= 0:
            messages.error(request, "El monto debe ser mayor a 0.")
            return redirect('portal_caja')

        facturas_pendientes = Factura.objects.filter(
            instalacion__cliente=cliente, 
            estado__in=["pendiente", "parcial"]
        ).order_by("periodo_inicio")

        total_deuda = sum([factura.saldo_pendiente for factura in facturas_pendientes])

        if monto_recibido > total_deuda:
            monto_str = f"{monto_recibido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if monto_str.endswith(",00"): monto_str = monto_str[:-3]
            deuda_str = f"{total_deuda:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if deuda_str.endswith(",00"): deuda_str = deuda_str[:-3]

            messages.error(request, f"Error: El monto ingresado ($ {monto_str}) supera la deuda total del cliente ($ {deuda_str}).")
            return redirect(f"/caja/?q={cliente.pk}")

        transaccion = Transaccion.objects.create(
            cliente=cliente,
            monto_total=monto_recibido,
            metodo_pago=metodo,
            fecha_pago=timezone.now().date()
        )

        monto_restante = monto_recibido

        for factura in facturas_pendientes:
            if monto_restante <= 0:
                break

            saldo_factura = factura.saldo_pendiente
            monto_a_aplicar = min(monto_restante, saldo_factura)

            Pago.objects.create(
                factura=factura,
                transaccion=transaccion,
                monto_pagado=monto_a_aplicar,
                tipo_pago="mensualidad"
            )

            monto_restante -= monto_a_aplicar

        monto_str = f"{monto_recibido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if monto_str.endswith(",00"):
            monto_str = monto_str[:-3]

        url_recibo = reverse("descargar_recibo_transaccion", args=[transaccion.pk])
        msg = f"Pago de <b>$ {monto_str}</b> procesado correctamente. &nbsp;&nbsp;&nbsp; <a href='{url_recibo}' target='_blank' style='text-decoration: underline; font-weight: 600;'>Imprimir comprobante</a>"

        messages.success(request, mark_safe(msg))
        return redirect(f"/caja/?q={cliente.pk}")

    q = request.GET.get('q', '').strip()
    if q:
        query = Q(nombre_completo__icontains=q)
        if q.isdigit():
            query |= Q(pk=q)

        cliente_encontrado = Cliente.objects.annotate(
            nombre_completo=Concat('nombre', Value(' '), 'apellido')
        ).filter(query).first()

        if cliente_encontrado:
            facturas_pendientes = Factura.objects.filter(
                instalacion__cliente=cliente_encontrado, 
                estado__in=["pendiente", "parcial"]
            ).order_by("periodo_inicio")

            total_deuda = sum([factura_pendiente.saldo_pendiente for factura_pendiente in facturas_pendientes])

            context.update({
                'cliente': cliente_encontrado,
                'facturas_pendientes': facturas_pendientes,
                'total_adeudado': total_deuda,
                'q': f"{cliente_encontrado.nombre} {cliente_encontrado.apellido}",
            })
        else:
            messages.warning(request, f"No se encontró ningún cliente coincidente con '{q}'.")

    return render(request, 'admin/caja_portal.html', context)
