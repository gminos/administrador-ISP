from django.contrib.admin.views.decorators import staff_member_required
from facturacion.tasks import procesar_envio_comprobando_whatsapp
from django.shortcuts import get_object_or_404, render, redirect
from facturacion.models import Transaccion, Cargo, DetallePago
from django.db.models import Value, Case, When, IntegerField
from redes.tasks import verificar_y_reactivar_instalacion
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.db.models.functions import Concat
from django.http import HttpResponse
from clientes.models import Cliente
from django.contrib import messages
from django.utils import timezone
from django.contrib import admin
from django.urls import reverse
from django.db.models import Q
from django.views import View
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


@method_decorator(staff_member_required, name='dispatch')
class PortalCajaView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        context = admin.site.each_context(request)
        context.update({'title': 'Caja rápida'})

        q = request.GET.get('q', '').strip()
        if q:
            query = Q(nombre_completo__icontains=q)
            if q.isdigit():
                query |= Q(pk=q)

            cliente_encontrado = Cliente.objects.annotate(
                nombre_completo=Concat('nombre', Value(' '), 'apellido')
            ).filter(query).first()

            if cliente_encontrado:
                cargos_pendientes = Cargo.objects.filter(
                    cliente=cliente_encontrado,
                    estado__in=["pendiente", "parcial"]
                ).annotate(
                    prioridad=Case(
                        When(tipo_cargo='mensualidad', then=1),
                        When(tipo_cargo='reconexion', then=2),
                        When(tipo_cargo='instalacion', then=3),
                        default=4,
                        output_field=IntegerField(),
                    )
                ).order_by("prioridad", "fecha_emision")

                deuda_total = sum(cargo.saldo_pendiente for cargo in cargos_pendientes)

                context.update({
                    "cliente": cliente_encontrado,
                    "cargos_pendientes": cargos_pendientes,
                    "total_deuda": deuda_total,
                    "q": f"{cliente_encontrado.nombre} {cliente_encontrado.apellido}"
                })
            else:
                messages.warning(request, f"No se encontró ningún cliente coincidente con '{q}'.")

        return render(request, 'admin/caja_portal.html', context)

    @staticmethod
    def post(request, *args, **kwargs):
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

        cargos_pendientes = Cargo.objects.filter(
            cliente=cliente,
            estado__in=["pendiente", "parcial"]
        ).annotate(
            prioridad=Case(
                When(tipo_cargo='mensualidad', then=1),
                When(tipo_cargo='reconexion', then=2),
                When(tipo_cargo='instalacion', then=3),
                default=4,
                output_field=IntegerField(),
            )
        ).order_by("prioridad", "fecha_emision")

        deuda_total = cliente.calcular_deuda_total()

        if monto_recibido > deuda_total:
            monto_str = f"{monto_recibido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if monto_str.endswith(",00"): monto_str = monto_str[:-3]
            deuda_str = f"{deuda_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if deuda_str.endswith(",00"): deuda_str = deuda_str[:-3]

            messages.error(request, f"Error: El monto ingresado ($ {monto_str}) supera la deuda total del cliente ($ {deuda_str}).")
            return redirect(f"/caja/?q={cliente.pk}")

        transaccion = Transaccion.objects.create(
            cliente=cliente,
            monto_total=monto_recibido,
            metodo_pago=metodo,
            fecha_pago=timezone.localdate()
        )

        monto_restante = monto_recibido
        detalle_pagos_nuevos = []
        cargos_modificados = []

        for cargo in cargos_pendientes:
            if monto_restante <= 0:
                break

            saldo_cargo = cargo.saldo_pendiente
            saldo_previo = cargo.saldo_pendiente
            monto_a_aplicar = min(monto_restante, saldo_cargo)

            cargo.saldo_pendiente -= monto_a_aplicar

            detalle_pagos_nuevos.append(DetallePago(
                transaccion=transaccion, 
                cargo=cargo, 
                monto_abonado=monto_a_aplicar,
                saldo_previo=saldo_previo,
                saldo_restante=cargo.saldo_pendiente
            ))

            monto_restante -= monto_a_aplicar

            if cargo.saldo_pendiente <= 0:
                cargo.estado = "pagado"
            elif cargo.saldo_pendiente < cargo.monto_total:
                cargo.estado = "parcial"

            cargos_modificados.append(cargo)

        DetallePago.objects.bulk_create(detalle_pagos_nuevos)
        Cargo.objects.bulk_update(cargos_modificados, ["estado", "saldo_pendiente"])

        procesar_envio_comprobando_whatsapp.delay(transaccion.pk, request.tenant.schema_name)
        
        for instalacion in cliente.instalaciones.filter(servicio_activo=False):
            verificar_y_reactivar_instalacion.delay(instalacion.pk, request.tenant.schema_name)

        monto_str = f"{monto_recibido:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if monto_str.endswith(",00"):
            monto_str = monto_str[:-3]

        url_recibo = reverse("descargar_recibo_transaccion", args=[transaccion.pk])
        msg = f"Pago de <b>$ {monto_str}</b> procesado correctamente. &nbsp;&nbsp;&nbsp; <a href='{url_recibo}' target='_blank' style='text-decoration: underline; font-weight: 600;'>Imprimir comprobante</a>"

        messages.success(request, mark_safe(msg))
        return redirect(f"/caja/?q={cliente.pk}")
