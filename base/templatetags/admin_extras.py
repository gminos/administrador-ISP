from django import template
import calendar
import logging
from base.admin import admin_site

register = template.Library()

@register.filter
def es_month_name(month_number):
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    try:
        return months.get(int(month_number), "")
    except (ValueError, TypeError):
        return ""

@register.filter
def clean_date_title(title):
    import re
    title = str(title)
    # Remove " de <Year>" pattern (e.g. " de 2025")
    title = re.sub(r' de \d{4}', '', title)
    # Remove "1 de " pattern (e.g. "1 de noviembre")
    title = re.sub(r'^1 de ', '', title)
    return title.capitalize()

@register.filter
def get_year_from_link(link):
    from urllib.parse import urlparse, parse_qs
    try:
        parsed_url = urlparse(link)
        query_params = parse_qs(parsed_url.query)
        year = query_params.get('periodo_inicio__year', [None])[0]
        return year if year else ""
    except Exception:
        return ""

@register.simple_tag(takes_context=True)
def has_multiple_years(context):
    # Try to get request from context dict or attribute
    request = context.get('request')
    if not request and hasattr(context, 'request'):
        request = context.request
        
    if not request:
        return True # Without request we cannot filter
    
    path = request.path
    for model, model_admin in admin_site._registry.items():
        meta = model._meta
        # Check standard admin path structure: /app/model/
        url_part = f"/{meta.app_label}/{meta.model_name}/"
        if url_part in path:
            date_field = getattr(model_admin, 'date_hierarchy', None)
            if date_field:
                try:
                    qs = model_admin.get_queryset(request)
                    dates_qs = qs.dates(date_field, 'year')
                    return dates_qs.count() > 1
                except Exception:
                    pass
    return True
