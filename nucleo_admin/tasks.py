from nucleo_admin.models import EmpresaISP
from django.utils import timezone
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def verificar_estado_isps(self):
    hoy = timezone.now().date()
    empresas = EmpresaISP.objects.all()

    for empresa in empresas:
        if empresa.fecha_proximo_pago:
            if hoy > empresa.fecha_proximo_pago:
                dias_retraso = (hoy - empresa.fecha_proximo_pago).days

                if dias_retraso > empresa.dias_gracia:
                    if empresa.estado_cuenta != 'suspendida':
                        empresa.estado_cuenta = 'suspendida'
                        empresa.save(update_fields=['estado_cuenta'])
                        logger.info(f"EmpresaISP {empresa.name} ha sido SUSPENDIDA por falta de pago.")
                else:
                    if empresa.estado_cuenta == 'activa':
                        empresa.estado_cuenta = 'mora'
                        empresa.save(update_fields=['estado_cuenta'])
                        logger.info(f"EmpresaISP {empresa.name} está en MORA. Días de gracia restantes: {empresa.dias_gracia - dias_retraso}")
            else:
                pass

    return "Verificación de estado de ISPs finalizada."


@shared_task(bind=True)
def enviar_correo_bienvenida_isp(self, email_destino, nombre_empresa, url_panel, password_temporal):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings
    
    subject = f'Bienvenido a NucleoISP - Credenciales de acceso para {nombre_empresa}'
    from_email = settings.DEFAULT_FROM_EMAIL
    
    context = {
        'nombre_empresa': nombre_empresa,
        'url_panel': url_panel,
        'email_destino': email_destino,
        'password_temporal': password_temporal,
    }
    
    html_content = render_to_string('nucleo_admin/emails/bienvenida_isp.html', context)
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email_destino])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        logger.info(f"Correo de bienvenida enviado exitosamente a {email_destino}")
        return True
    except Exception as e:
        logger.error(f"Error enviando correo de bienvenida a {email_destino}: {str(e)}")
        return False
