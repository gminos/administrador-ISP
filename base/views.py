from django.utils.translation import gettext_lazy as _
from clientes.models import Cliente
from facturacion.models import Cargo, DetallePago, Transaccion
from instalaciones.models import Instalacion
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth

def dashboard_callback(request, context):
    total_clientes = Cliente.objects.count()
    total_instalaciones = Instalacion.objects.count()
    total_servicios_activos = Instalacion.objects.filter(servicio_activo=True).count()

    total_recaudado = DetallePago.objects.aggregate(
        total=Sum("monto_abonado")
    )["total"] or 0

    total_inst_revenue = Instalacion.objects.aggregate(
        total=Sum("costo")
    )["total"] or 0

    current_year = timezone.now().year
    total_inst_revenue_year = Instalacion.objects.filter(
        fecha_instalacion__year=current_year
    ).aggregate(total=Sum("costo"))["total"] or 0

    instalaciones_anio = Instalacion.objects.filter(
        fecha_instalacion__year=current_year,
        servicio_activo=True
    ).count()

    META_SERVICIOS = 100
    progreso_meta = min((total_servicios_activos / META_SERVICIOS) * 100, 100)
    falta_meta = max(META_SERVICIOS - total_servicios_activos, 0)

    last_12_months = timezone.now() - timedelta(days=365)
    pagos_por_mes = Transaccion.objects.filter(
        fecha_pago__gte=last_12_months
    ).annotate(
        month=TruncMonth('fecha_pago')
    ).values('month').annotate(
        total=Sum('monto_total')
    ).order_by('month')

    labels = []
    data = []

    for pago in pagos_por_mes:
        labels.append(pago['month'].strftime('%B %Y'))
        data.append(float(pago['total']))

    from django.db.models import Count

    instalaciones_por_mes = Instalacion.objects.filter(
        fecha_instalacion__gte=last_12_months
    ).annotate(
        month=TruncMonth('fecha_instalacion')
    ).values('month').annotate(
        total=Count('id'),
        revenue=Sum('costo')
    ).order_by('month')

    inst_labels = []
    inst_count = []
    inst_revenue = []

    for inst in instalaciones_por_mes:
        inst_labels.append(inst['month'].strftime('%B %Y'))
        inst_count.append(inst['total'])
        inst_revenue.append(float(inst['revenue']))

    deuda_total = Cargo.objects.filter(estado__in=["pendiente", "parcial"]).aggregate(
        total=Sum("saldo_pendiente")
    )["total"] or 0

    ingresos_metodo_qs = Transaccion.objects.values("metodo_pago").annotate(total=Sum("monto_total"))

    ingresos_por_metodo = []
    colores_metodo = {"efectivo": "#10b981", "transferencia": "#3b82f6"}

    for item in ingresos_metodo_qs:
        metodo = item["metodo_pago"]
        if metodo and metodo != "no aplica":
            ingresos_por_metodo.append({
                "label": metodo.capitalize(),
                "data": float(item["total"] or 0),
                "color": colores_metodo.get(metodo.lower(), "#6b7280")
            })

    ingresos_metodo_labels = [item["label"] for item in ingresos_por_metodo]
    ingresos_metodo_data = [item["data"] for item in ingresos_por_metodo]

    planes_dist_qs = Instalacion.objects.filter(servicio_activo=True).values("plan__nombre").annotate(total=Count("id"))
    planes_labels = [item["plan__nombre"] for item in planes_dist_qs]
    planes_data = [item["total"] for item in planes_dist_qs]

    veredas_dist_qs = Instalacion.objects.filter(servicio_activo=True).values("cliente__vereda").annotate(total=Count("id"))
    veredas_labels = [item["cliente__vereda"] for item in veredas_dist_qs if item["cliente__vereda"]]
    veredas_data = [item["total"] for item in veredas_dist_qs if item["cliente__vereda"]]

    import json
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
        "chart_labels": json.dumps(labels),
        "chart_data": json.dumps(data),
        "inst_labels": json.dumps(inst_labels),
        "inst_count": json.dumps(inst_count),
        "inst_revenue": json.dumps(inst_revenue),
        "payment_method_labels": json.dumps(ingresos_metodo_labels),
        "payment_method_data": json.dumps(ingresos_metodo_data),
        "plans_labels": json.dumps(planes_labels),
        "plans_data": json.dumps(planes_data),
        "veredas_labels": json.dumps(veredas_labels),
        "veredas_data": json.dumps(veredas_data),
    })
    return context
