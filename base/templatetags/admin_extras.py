from django import template

register = template.Library()

@register.filter
def clean_month(value):
    if " de " in value:
        parts = value.split(" de ")
        if len(parts) == 2 and parts[1].isdigit():
            return parts[0]
    return value

@register.filter
def is_year(value):
    if not value:
        return False
    return str(value).strip().isdigit() and len(str(value).strip()) == 4
