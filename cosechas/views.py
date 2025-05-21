# cosechas/views.py
"""
Vistas funcionales REST para la gestión de cultivos y cosechas.
Cada operación está separada y documentada:
- Listado, creación, actualización, eliminación.
- Control de acceso autenticado.
- Validación explícita y contexto para trazabilidad del usuario.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cultivo, Cosecha
from .serializers import CultivoSerializer, CosechaSerializer, CosechaDetalleSerializer


# ────────────────────────────────────────────────────────────────
# 🌱 CULTIVOS – LISTADO Y REGISTRO
# ────────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_cultivos(request):
    """
    GET /cultivos/  ➜ Lista todos los cultivos ordenados por nombre.
    """
    cultivos = Cultivo.objects.all().order_by("nombre")
    serializer = CultivoSerializer(cultivos, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def registrar_cultivo(request):
    """
    POST /cultivos/  ➜ Crea un nuevo cultivo.
    """
    serializer = CultivoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# 🚜 COSECHAS – LISTADO Y REGISTRO
# ────────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def listar_cosechas(request):
    """
    GET /cosechas/  ➜ Lista todas las cosechas con detalle.
    """
    cosechas = Cosecha.objects.select_related("cultivo", "registrado_por").order_by("-fecha_fin_cosecha")
    serializer = CosechaDetalleSerializer(cosechas, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def registrar_cosecha(request):
    """
    POST /cosechas/  ➜ Registra una nueva cosecha.
    """
    serializer = CosechaSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save(registrado_por=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# 🧾 COSECHA DETALLE – GET, PUT, PATCH, DELETE
# ────────────────────────────────────────────────────────────────
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def detalle_cosecha(request, pk):
    """
    GET /cosechas/<pk>/  ➜ Obtiene el detalle de una cosecha.
    """
    cosecha = get_object_or_404(Cosecha.objects.select_related("cultivo", "registrado_por"), pk=pk)
    serializer = CosechaDetalleSerializer(cosecha)
    return Response(serializer.data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def actualizar_cosecha(request, pk):
    """
    PUT/PATCH /cosechas/<pk>/  ➜ Actualiza los datos de una cosecha.
    """
    cosecha = get_object_or_404(Cosecha, pk=pk)
    partial = request.method == "PATCH"
    serializer = CosechaSerializer(cosecha, data=request.data, partial=partial, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def eliminar_cosecha(request, pk):
    """
    DELETE /cosechas/<pk>/  ➜ Elimina una cosecha existente.
    """
    cosecha = get_object_or_404(Cosecha, pk=pk)
    cosecha.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
