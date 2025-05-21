# control_calidad/views.py
"""
Vistas funcionales (FBV) para el módulo de Control de Calidad.
Incluyen:
- CRUD de lotes procesados
- Generación automática de PDF
- Envío de informe por correo en lote encriptado
- Seguridad, trazabilidad y logs
"""

import logging
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LoteProcesado
from .serializers import LoteProcesadoSerializer
from .utils import generar_pdf_lote, encriptar_con_cedula, enviar_informe_por_correo

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_lotes(request):
    """
    Lista todos los lotes procesados, ordenados por fecha.
    """
    lotes = LoteProcesado.objects.select_related('cliente').order_by('-fecha_procesamiento')
    serializer = LoteProcesadoSerializer(lotes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_lote(request):
    """
    Crea un nuevo lote procesado (control de calidad).
    """
    serializer = LoteProcesadoSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        logger.info(f"✅ Lote registrado por {request.user}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_lote(request, pk):
    """
    Devuelve los detalles de un lote específico por su ID.
    """
    lote = get_object_or_404(LoteProcesado.objects.select_related('cliente'), pk=pk)
    serializer = LoteProcesadoSerializer(lote)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_lote(request, pk):
    """
    Actualiza un lote completo (PUT) o parcialmente (PATCH).
    """
    lote = get_object_or_404(LoteProcesado, pk=pk)
    partial = request.method == 'PATCH'
    serializer = LoteProcesadoSerializer(
        lote, data=request.data, partial=partial, context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        logger.info(f"🛠️ Lote {pk} actualizado por {request.user}")
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_lote(request, pk):
    """
    Elimina un lote procesado.
    """
    lote = get_object_or_404(LoteProcesado, pk=pk)
    lote.delete()
    logger.warning(f"❌ Lote {pk} eliminado por {request.user}")
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_informe_pdf(request, pk):
    """
    Genera, encripta y envía un informe PDF por correo al cliente.
    """
    lote = get_object_or_404(LoteProcesado, pk=pk)
    cliente = lote.cliente

    # Validación: cédula requerida para encriptar
    if not getattr(cliente, 'cedula', None):
        logger.warning(f"⚠️ Cliente sin cédula. Lote {pk} no puede enviarse.")
        return Response({"error": "El cliente no tiene cédula registrada."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        pdf = generar_pdf_lote(lote)
        pdf_encriptado, clave = encriptar_con_cedula(pdf, cliente.cedula)
        enviar_informe_por_correo(lote, pdf_encriptado)

        lote.enviado = True
        lote.save(update_fields=['enviado'])

        logger.info(f"📤 Informe de lote {pk} enviado correctamente a {cliente.email}")
        return Response({"mensaje": "Informe enviado exitosamente."}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"🚨 Error al generar/enviar informe del lote {pk}: {str(e)}")
        return Response({"error": "Error al procesar el informe.", "detalle": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
