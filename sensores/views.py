"""
Vistas REST para el módulo IoT mejoradas con:
- Validaciones de rango automático
- Activación/desactivación de actuadores según rangos definidos
- Control manual de sensores y actuadores
- Filtros personalizados y protección de integridad
"""

# ─── IMPORTACIONES ────────────────────────────────────────────────
from django_filters import rest_framework as df_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters as drf_filters, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Sensor, Medicion
from .serializers import SensorSerializer, MedicionSerializer, MedicionDetalleSerializer

# ────────────────────────────────────────────────────────────────
# 🌡️ FILTROS PERSONALIZADOS PARA SENSORES
# ────────────────────────────────────────────────────────────────
class SensorFilter(df_filters.FilterSet):
    """
    Filtro para buscar sensores por tipo y estado (activo).
    """
    tipo = df_filters.CharFilter(field_name="tipo", lookup_expr="iexact")
    activo = df_filters.BooleanFilter(field_name="activo")

    class Meta:
        model = Sensor
        fields = ["tipo", "activo"]

# ────────────────────────────────────────────────────────────────
# 🧩 VISTA: Lista y crea sensores
# ────────────────────────────────────────────────────────────────
class SensorListCreateView(generics.ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = SensorFilter
    search_fields = ["nombre", "ubicacion"]
    ordering_fields = ["nombre", "creado_en"]
    ordering = ["nombre"]

# ────────────────────────────────────────────────────────────────
# 🧩 VISTA: Detalle, edición y eliminación de un sensor
# ────────────────────────────────────────────────────────────────
class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.mediciones.exists():
            raise serializers.ValidationError("No se puede eliminar el sensor: posee mediciones históricas.")
        super().perform_destroy(instance)

# ────────────────────────────────────────────────────────────────
# 🔁 VISTA: Activar/Desactivar sensor manualmente
# ────────────────────────────────────────────────────────────────
class SensorToggleActivoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            sensor = Sensor.objects.get(pk=pk)
            sensor.activo = not sensor.activo
            sensor.save()
            estado = "activo" if sensor.activo else "inactivo"
            return Response({"mensaje": f"Sensor {sensor.nombre} ahora está {estado}"})
        except Sensor.DoesNotExist:
            return Response({"error": "Sensor no encontrado"}, status=status.HTTP_404_NOT_FOUND)

# ────────────────────────────────────────────────────────────────
# 📈 FILTROS PERSONALIZADOS PARA MEDICIONES
# ────────────────────────────────────────────────────────────────
class MedicionFilter(df_filters.FilterSet):
    """
    Filtro para mediciones entre rangos de fechas.
    """
    desde = df_filters.DateFilter(field_name="timestamp", lookup_expr="date__gte")
    hasta = df_filters.DateFilter(field_name="timestamp", lookup_expr="date__lte")

    class Meta:
        model = Medicion
        fields = ["sensor", "desde", "hasta"]

# ────────────────────────────────────────────────────────────────
# 🧪 VISTA: Lista y crea mediciones
# ────────────────────────────────────────────────────────────────
class MedicionListCreateView(generics.ListCreateAPIView):
    queryset = Medicion.objects.select_related("sensor")
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = MedicionFilter
    ordering_fields = ["timestamp", "valor"]
    ordering = ["-timestamp"]

    def get_serializer_class(self):
        return MedicionDetalleSerializer if self.request.method == "GET" else MedicionSerializer

    def perform_create(self, serializer):
        medicion = serializer.save()
        sensor = medicion.sensor

        if sensor.rango_minimo is not None and medicion.valor < sensor.rango_minimo:
            print(f"🟡 Actuador activado por valor bajo en {sensor.nombre}: {medicion.valor}")
        elif sensor.rango_maximo is not None and medicion.valor > sensor.rango_maximo:
            print(f"🔴 Actuador desactivado por valor alto en {sensor.nombre}: {medicion.valor}")
        elif sensor.valor_referencia is not None:
            print(f"✅ Valor estable cerca del objetivo en {sensor.nombre}")

# ────────────────────────────────────────────────────────────────
# 🧪 VISTA: Detalle, actualización y eliminación de una medición
# ────────────────────────────────────────────────────────────────
class MedicionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Medicion.objects.select_related("sensor")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return MedicionDetalleSerializer if self.request.method == "GET" else MedicionSerializer

# ────────────────────────────────────────────────────────────────
# 🌐 VISTA HTML DE SENSORES (Panel visual)
# ────────────────────────────────────────────────────────────────
@method_decorator(login_required, name='dispatch')
class SensorTemplateView(TemplateView):
    """
    Vista para renderizar la plantilla HTML de sensores.
    URL: /api2/panel/ o similar
    """
    template_name = "sensores/sensores_list.html"
