from pywa.types.templates import HeaderImage, BodyText, TemplateLanguage
from django.template.loader import render_to_string
from facturacion.models import Factura, Transaccion
from facturacion.utils import generar_pdf_factura
from pdf2image import convert_from_bytes
from pywa.errors import WhatsAppError
from django.db import connection
from pywa import WhatsApp
from PIL import Image
import weasyprint
import logging
import io

def _unir_imagenes_vertical(images):
    if len(images) == 1:
        return images[0]
    widths, heights = zip(*(i.size for i in images))
    combined = Image.new('RGB', (max(widths), sum(heights)))
    y_offset = 0
    for img in images:
        combined.paste(img, (0, y_offset))
        y_offset += img.size[1]
    return combined

def enviar_factura_cliente(factura: Factura) -> bool:
    tenant = connection.tenant

    if not tenant.wa_token or not tenant.wa_phone_id:
        print(f"Error: El inquilino {tenant.name} no tiene configurado WhatsApp.")
        return False

    wa = WhatsApp(phone_id=tenant.wa_phone_id, token=tenant.wa_token)

    telefono_cliente = factura.cliente.telefono
    if not telefono_cliente:
        print(f"Error: El cliente {factura.cliente} no tiene telefono registrado.")
        return False

    telefono_limpio = "".join([c for c in str(telefono_cliente) if c.isdigit()])
    if len(telefono_limpio) == 10:
        telefono_limpio = f"57{telefono_limpio}"

    try:
        print(f"Generando PDF para Factura #{factura.pk}...")
        pdf_bytes = generar_pdf_factura(factura)

        print("Convirtiendo PDF a Imagen...")
        images = convert_from_bytes(pdf_bytes, dpi=200)
        if not images:
            raise ValueError("Error al convertir PDF a imagen")

        img_byte_arr = io.BytesIO()
        final_image = _unir_imagenes_vertical(images)
        final_image.save(img_byte_arr, format='JPEG')
        jpg_bytes = img_byte_arr.getvalue()

        print("Subiendo imagen a los servidores de WhatsApp...")
        media_id = wa.upload_media(
            media=jpg_bytes,
            mime_type="image/jpeg",
            media_type="image",
            filename=f"Factura_Arint_{factura.pk}.jpg"
        )

        nombre_cliente = f"{factura.cliente.nombre} {factura.cliente.apellido}"
        mes_facturado = factura.periodo_inicio.strftime('%B %Y') if factura.periodo_inicio else "este mes"
        total_a_pagar = factura.cliente.calcular_deuda_total()
        total_a_pagar_str = f"${total_a_pagar:,.0f}"

        print(f"Enviando plantilla a {telefono_limpio}...")

        wa.send_template(
            to=telefono_limpio,
            name="envio_factura_mensual_v2",
            language=TemplateLanguage.SPANISH_CO,
            params=[
                HeaderImage.params(
                    image=media_id.id
                ),
                BodyText.params(nombre_cliente, mes_facturado, total_a_pagar_str)
            ]
        )

        print("Mensaje enviado con exito")
        return True
    except WhatsAppError as e:
        logging.error(f"Error de API de WhatsApp enviando factura a {telefono_cliente}: {e}", exc_info=True)
        return False
    except (ValueError, OSError, TypeError, RuntimeError) as e:
        logging.error(f"Error interno generando/enviando factura a {telefono_cliente}", exc_info=True)
        return False

def generar_pdf_comprobante(transaccion: Transaccion) -> bytes:
    from django.db import connection
    tenant = connection.tenant
    html_string = render_to_string('facturacion/recibo_transaccion_pdf.html', {'transaccion': transaccion, 'tenant': tenant})
    html = weasyprint.HTML(string=html_string)
    return html.write_pdf()

def enviar_comprobante_pago(transaccion: Transaccion) -> bool:
    tenant = connection.tenant

    if not tenant.wa_token or not tenant.wa_phone_id:
        print(f"Error: El inquilino {tenant.name} no tiene configurado WhatsApp.")
        return False

    wa = WhatsApp(phone_id=tenant.wa_phone_id, token=tenant.wa_token)

    telefono_cliente = transaccion.cliente.telefono
    if not telefono_cliente:
        return False

    telefono_limpio = "".join([c for c in str(telefono_cliente) if c.isdigit()])
    if len(telefono_limpio) == 10:
        telefono_limpio = f"57{telefono_limpio}"

    try:
        pdf_bytes = generar_pdf_comprobante(transaccion)
        images = convert_from_bytes(pdf_bytes, dpi=200)

        if not images:
            raise ValueError("Error al convertir PDF a imagen")

        img_byte_arr = io.BytesIO()
        final_image = _unir_imagenes_vertical(images)
        final_image.save(img_byte_arr, format='JPEG')
        jpg_bytes = img_byte_arr.getvalue()

        media_id = wa.upload_media(
            media=jpg_bytes,
            mime_type="image/jpeg",
            media_type="image",
            filename=f"Comprobante_Pago_{transaccion.pk}.jpg"
        )

        nombre_cliente = f"{transaccion.cliente.nombre} {transaccion.cliente.apellido}"
        monto_pagado_str = f"${transaccion.monto_total:,.0f}"

        wa.send_template(
            to=telefono_limpio,
            name="enviar_comprobante_pago_v2",
            language=TemplateLanguage.SPANISH_CO,
            params=[
                HeaderImage.params(
                    image=media_id.id
                ),
                BodyText.params(nombre_cliente, monto_pagado_str)
            ]
        )
        return True
    except WhatsAppError as e:
        logging.error(f"Error de API de WhatsApp enviando recibo a {telefono_cliente}: {e}", exc_info=True)
        return False
    except (ValueError, OSError, TypeError, RuntimeError) as e:
        logging.error(f"Error interno generando/enviando recibo a {telefono_cliente}", exc_info=True)
        return False
