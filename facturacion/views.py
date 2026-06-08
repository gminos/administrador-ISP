from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from facturacion.models import Pago
from django.contrib.admin.views.decorators import staff_member_required
import weasyprint

@staff_member_required
def descargar_comprobante_pdf_view(request, pago_id):
    pago = get_object_or_404(Pago, pk=pago_id)
    html_string = render_to_string('facturacion/comprobante_pdf.html', {'pago': pago})
    html = weasyprint.HTML(string=html_string)
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="comprobante_{pago.pk}.pdf"'
    return response
