from django.utils import timezone

def get_nuevo_badge(request):
    if timezone.now().date() <= timezone.datetime(2026, 7, 15).date():
        return "Nuevo"
    return ""
