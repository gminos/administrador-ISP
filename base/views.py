from django.utils.translation import gettext_lazy as _
from clientes.models import Cliente
from facturacion.models import Factura, Pago
from instalaciones.models import Intalacion
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth

def dashboard_callback(request, context):
    total_clientes = Cliente.objects.count()
    total_instalaciones = Intalacion.objects.count()
    total_servicios_activos = Intalacion.objects.filter(servicio_activo=True).count()
    
    total_recaudado = Pago.objects.filter(estado="pagado").aggregate(
        total=Sum("monto_pagado")
    )["total"] or 0

    total_inst_revenue = Intalacion.objects.aggregate(
        total=Sum("costo")
    )["total"] or 0

    current_year = timezone.now().year
    total_inst_revenue_year = Intalacion.objects.filter(
        fecha_instalacion__year=current_year
    ).aggregate(total=Sum("costo"))["total"] or 0

    instalaciones_anio = Intalacion.objects.filter(
        fecha_instalacion__year=current_year,
        servicio_activo=True
    ).count()

    META_SERVICIOS = 100
    progreso_meta = min((total_servicios_activos / META_SERVICIOS) * 100, 100)
    falta_meta = max(META_SERVICIOS - total_servicios_activos, 0)
    
    last_12_months = timezone.now() - timedelta(days=365)
    pagos_por_mes = Pago.objects.filter(
        factura__periodo_final__gte=last_12_months,
        estado="pagado"
    ).annotate(
        month=TruncMonth('factura__periodo_final')
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

    deuda_total = Pago.objects.filter(estado="pendiente").aggregate(
        total=Sum("monto_pagado")
    )["total"] or 0

    ingresos_metodo_qs = Pago.objects.filter(estado="pagado").values("metodo_pago").annotate(total=Sum("monto_pagado"))
    ingresos_metodo_labels = [item["metodo_pago"].capitalize() for item in ingresos_metodo_qs]
    ingresos_metodo_data = [float(item["total"]) for item in ingresos_metodo_qs]

    planes_dist_qs = Intalacion.objects.filter(servicio_activo=True).values("plan__nombre").annotate(total=Count("instalacion_id"))
    planes_labels = [item["plan__nombre"] for item in planes_dist_qs]
    planes_data = [item["total"] for item in planes_dist_qs]

    veredas_dist_qs = Intalacion.objects.filter(servicio_activo=True).values("cliente__vereda").annotate(total=Count("instalacion_id"))
    veredas_labels = [item["cliente__vereda"] for item in veredas_dist_qs if item["cliente__vereda"]]
    veredas_data = [item["total"] for item in veredas_dist_qs if item["cliente__vereda"]]

    context.update({
        "kpi_data": {
            "clientes": {
                "title": "Total clientes",
                "metric": total_clientes,
                "footer": "Registrados en el sistema",
            },
            "instalaciones": {
                "title": "Total de instalaciones",
                "metric": total_instalaciones,
                "footer": "",
                "year_title": "Instalaciones en año actual",
                "year_metric": instalaciones_anio,
                "year_footer": "",
            },
            "recaudo": {
                "title": "Total en pagos confirmados",
                "metric": f"${total_recaudado:,.2f}",
                "footer": "",
            },
            "deuda": {
                "title": "Total en pagos pendientes",
                "metric": f"${deuda_total:,.2f}",
                "footer": "",
            },
            "inst_revenue": {
                "title": "Total en instalaciones",
                "metric": f"${total_inst_revenue:,.2f}",
                "footer": "",
                "year_title": "Total en año actual",
                "year_metric": f"${total_inst_revenue_year:,.2f}",
                "year_footer": "",
            },

        },
        "meta_data": {
            "progreso": f"{progreso_meta:.1f}",
            "falta": falta_meta,
            "total": META_SERVICIOS,
            "actual": total_servicios_activos
        },
        "chart_labels": labels,
        "chart_data": data,
        "inst_labels": inst_labels,
        "inst_count": inst_count,
        "inst_revenue": inst_revenue,
        "payment_method_labels": ingresos_metodo_labels,
        "payment_method_data": ingresos_metodo_data,
        "plans_labels": planes_labels,
        "plans_data": planes_data,
        "veredas_labels": veredas_labels,
        "veredas_data": veredas_data,
    })
    return context
