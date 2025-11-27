from django.utils.translation import gettext_lazy as _
from clientes.models import Cliente
from facturacion.models import Factura, Pago
from instalaciones.models import Intalacion
from django.db.models import Sum

def dashboard_callback(request, context):
    total_clientes = Cliente.objects.count()
    total_instalaciones = Intalacion.objects.filter(servicio_activo=True).count()
    
    total_recaudado = Pago.objects.filter(estado="pagado").aggregate(
        total=Sum("monto_pagado")
    )["total"] or 0

    from django.utils import timezone
    from datetime import timedelta
    from django.db.models.functions import TruncMonth
    
    last_12_months = timezone.now() - timedelta(days=365)
    pagos_por_mes = Pago.objects.filter(
        fecha_pago__gte=last_12_months,
        estado="pagado"
    ).annotate(
        month=TruncMonth('fecha_pago')
    ).values('month').annotate(
        total=Sum('monto_pagado')
    ).order_by('month')

    labels = []
    data = []
    
    for pago in pagos_por_mes:
        labels.append(pago['month'].strftime('%B %Y'))
        data.append(float(pago['total']))

    from django.db.models import Count
    
    instalaciones_por_mes = Intalacion.objects.filter(
        fecha_instalacion__gte=last_12_months
    ).annotate(
        month=TruncMonth('fecha_instalacion')
    ).values('month').annotate(
        total=Count('instalacion_id'),
        revenue=Sum('costo')
    ).order_by('month')

    inst_labels = []
    inst_count = []
    inst_revenue = []

    for inst in instalaciones_por_mes:
        inst_labels.append(inst['month'].strftime('%B %Y'))
        inst_count.append(inst['total'])
        inst_revenue.append(float(inst['revenue']))

    context.update({
        "kpi_data": {
            "clientes": {
                "title": "Total Clientes",
                "metric": total_clientes,
                "footer": "Registrados en el sistema",
            },
            "instalaciones": {
                "title": "Instalaciones Activas",
                "metric": total_instalaciones,
                "footer": "Servicios operando",
            },
            "recaudo": {
                "title": "Total Recaudado",
                "metric": f"${total_recaudado:,.2f}",
                "footer": "Pagos confirmados",
            },
        },
        "chart_labels": labels,
        "chart_data": data,
        "inst_labels": inst_labels,
        "inst_count": inst_count,
        "inst_revenue": inst_revenue,
    })
    return context
