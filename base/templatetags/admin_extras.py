from django import template
import calendar

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
