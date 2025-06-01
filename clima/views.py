# clima/views.py
"""
Vistas RESTful para dispositivos y lecturas climáticas.
Mejoras:
- Métodos individuales por función
- Comentarios detallados
- Control estructurado de errores
- Separación de responsabilidades
- Preparado para lógica automatizada futura
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import DispositivoClima, LecturaClima
from .serializers import (
    DispositivoClimaSerializer,
    LecturaClimaSerializer,
    LecturaClimaDetalleSerializer
)

# ╭────────────────────────────────────────────────────────────╮
# │ DISPOSITIVO CLIMÁTICO – CRUD                              │
# ╰────────────────────────────────────────────────────────────╯

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_dispositivos(request):
    dispositivos = DispositivoClima.objects.all()
    serializer = DispositivoClimaSerializer(dispositivos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_dispositivo(request):
    serializer = DispositivoClimaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_dispositivo(request, pk):
    dispositivo = get_object_or_404(DispositivoClima, pk=pk)
    serializer = DispositivoClimaSerializer(dispositivo)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_dispositivo(request, pk):
    dispositivo = get_object_or_404(DispositivoClima, pk=pk)
    partial = request.method == 'PATCH'
    serializer = DispositivoClimaSerializer(dispositivo, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_dispositivo(request, pk):
    dispositivo = get_object_or_404(DispositivoClima, pk=pk)
    dispositivo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ╭────────────────────────────────────────────────────────────╮
# │ LECTURA CLIMÁTICA – CRUD                                  │
# ╰────────────────────────────────────────────────────────────╯

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_lecturas(request):
    lecturas = LecturaClima.objects.select_related("dispositivo").all()
    serializer = LecturaClimaDetalleSerializer(lecturas, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_lectura(request):
    serializer = LecturaClimaSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_lectura(request, pk):
    lectura = get_object_or_404(LecturaClima, pk=pk)
    serializer = LecturaClimaDetalleSerializer(lectura)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def actualizar_lectura(request, pk):
    lectura = get_object_or_404(LecturaClima, pk=pk)
    partial = request.method == 'PATCH'
    serializer = LecturaClimaSerializer(lectura, data=request.data, partial=partial)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_lectura(request, pk):
    lectura = get_object_or_404(LecturaClima, pk=pk)
    lectura.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
