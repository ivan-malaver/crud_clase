# control_calidad/utils.py
"""
Utilidades para generación, encriptación y envío de informes PDF de LoteProcesado
────────────────────────────────────────────────────────────────────────
Mejoras y ajustes:
1. Constantes para configuración de página y márgenes               📐
2. Context manager (`with`) para manejar BytesIO y canvas           🔄
3. Formato de fecha legible usando `strftime`                       🗓️
4. Validaciones tempranas y mensajes claros                          🔍
5. Diversión de plantillas HTML + texto plano con `EmailMultiAlternatives`  ✉️
6. Logging de errores en email y encriptación                       🛠️
7. Uso de `get_full_name()` con fallback a `username`               👤
"""
import io
import base64
import hashlib
import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from cryptography.fernet import Fernet

# Logger para reportar errores de utils
logger = logging.getLogger(__name__)

# Constantes de diseño PDF
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 50
LINE_HEIGHT = 18


def generar_pdf_lote(lote) -> bytes:
    """
    Genera un PDF con datos de calidad del lote.
    Retorna el contenido en bytes.
    """
    buffer = io.BytesIO()
    # Context manager asegura flush y close
    with canvas.Canvas(buffer, pagesize=A4) as p:
        y = PAGE_HEIGHT - MARGIN
        # Título
        p.setFont("Helvetica-Bold", 16)
        p.drawString(MARGIN, y, f"Informe de Calidad: Lote {lote.codigo_lote}")
        p.setFont("Helvetica", 12)
        y -= LINE_HEIGHT * 2

        # Mapa de campos a mostrar
        datos = [
            ("Cliente:", getattr(lote.cliente, 'get_full_name', lote.cliente.username)()),
            ("Tipo de grano:", lote.get_tipo_grano_display()),
            ("Procesado el:", lote.fecha_procesamiento.strftime("%Y-%m-%d")),
            ("Cantidad (kg):", f"{lote.cantidad_kg}"),
            ("Humedad (%):", f"{lote.humedad}"),
            ("Impurezas (%):", f"{lote.impurezas}"),
            ("Grano bueno (%):", f"{lote.grano_bueno}"),
            ("Grano defectuoso (%):", f"{lote.grano_defectuoso}"),
        ]
        for etiqueta, valor in datos:
            p.drawString(MARGIN, y, f"{etiqueta} {valor}")
            y -= LINE_HEIGHT

        # Observaciones si existen
        if lote.observaciones:
            y -= LINE_HEIGHT
            p.drawString(MARGIN, y, "Observaciones:")
            for linea in lote.observaciones.splitlines():
                y -= LINE_HEIGHT
                p.drawString(MARGIN + 20, y, linea)

        p.showPage()
        p.save()

    buffer.seek(0)
    return buffer.getvalue()


def encriptar_con_cedula(pdf_bytes: bytes, cedula: str) -> tuple[bytes, bytes]:
    """
    Encripta `pdf_bytes` usando SHA256(cedula) como clave para Fernet.
    Devuelve (datos_encriptados, clave_base64).
    """
    if not cedula:
        raise ValueError("Cédula de usuario requerida para encriptar PDF.")
    # Derivar clave de 32 bytes
    key_raw = hashlib.sha256(cedula.encode('utf-8')).digest()
    key = base64.urlsafe_b64encode(key_raw)
    f = Fernet(key)
    token = f.encrypt(pdf_bytes)
    return token, key


def enviar_informe_por_correo(lote, pdf_bytes: bytes) -> None:
    """
    Envía un email con PDF adjunto al cliente.
    Usa HTML y texto plano.
    Actualiza `lote.enviado` a True.
    """
    email_destino = getattr(lote.cliente, 'email', None)
    if not email_destino:
        raise ValueError("El cliente no tiene dirección de correo registrada.")

    subject = f"Informe Calidad Lote {lote.codigo_lote}"
    # Contexto para plantilla
    contexto = {
        'cliente': getattr(lote.cliente, 'get_full_name', lote.cliente.username)(),
        'codigo_lote': lote.codigo_lote,
        'fecha': lote.fecha_procesamiento,
    }
    # Generar cuerpo en HTML y texto plano
    html_body = render_to_string('control_calidad/email.html', contexto)
    text_body = render_to_string('control_calidad/email.txt', contexto)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email_destino],
    )
    email.attach_alternative(html_body, 'text/html')
    email.attach(f"informe_{lote.codigo_lote}.pdf", pdf_bytes, 'application/pdf')

    try:
        email.send(fail_silently=False)
        lote.enviado = True
        lote.save(update_fields=['enviado'])
    except Exception as exc:
        logger.error(f"Error enviando informe lote {lote.codigo_lote}: {exc}")
        raise
