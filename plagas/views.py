# plagas/views.py
"""
Vistas RESTful tipo ViewSet para el módulo de plagas.
Cada método está separado, comentado y alineado con buenas prácticas:
- Serializador dinámico según la acción
- Permisos y filtros
- Endpoint adicional para validación manual de predicciones
"""

from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import mixins, viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import TipoPlaga, EventoPlaga, PrediccionPlaga
from .serializers import (
    TipoPlagaSerializer,
    EventoPlagaSerializer, EventoPlagaDetalleSerializer,
    PrediccionPlagaSerializer, PrediccionPlagaDetalleSerializer,
)

# ────────────────────────────────────────────────────────────────
# 🌿 TIPO DE PLAGA – CRUD COMPLETO
# ────────────────────────────────────────────────────────────────
class TipoPlagaViewSet(viewsets.ModelViewSet):
    """
    Vista CRUD para tipos de plaga.
    - GET    /plagas/tipos/
    - POST   /plagas/tipos/
    - GET    /plagas/tipos/<pk>/
    - PUT    /plagas/tipos/<pk>/
    - PATCH  /plagas/tipos/<pk>/
    - DELETE /plagas/tipos/<pk>/
    """
    queryset = TipoPlaga.objects.all().order_by("nombre")
    serializer_class = TipoPlagaSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Filtros y ordenamiento
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["cultivo_afectado", "temporada"]
    search_fields = ["nombre", "cultivo_afectado"]
    ordering_fields = ["nombre"]
    ordering = ["nombre"]


# ────────────────────────────────────────────────────────────────
# 🐛 EVENTO DE PLAGA – LECTURA Y REGISTRO
# ────────────────────────────────────────────────────────────────
class EventoPlagaFilter(FilterSet):
    class Meta:
        model = EventoPlaga
        fields = ["tipo", "severidad", "fecha_detectada"]


class EventoPlagaViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin):
    """
    Vista para eventos de plaga.
    - GET    /plagas/eventos/         → listado
    - POST   /plagas/eventos/         → crear evento
    - GET    /plagas/eventos/<pk>/    → ver detalle
    """
    queryset = EventoPlaga.objects.select_related("tipo", "registrado_por").all()
    permission_classes = [permissions.IsAuthenticated]

    # Filtros y búsqueda
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = EventoPlagaFilter
    ordering_fields = ["fecha_detectada", "severidad"]
    search_fields = ["ubicacion", "observaciones"]
    ordering = ["-fecha_detectada"]

    # Serializador dinámico según si es GET o POST
    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return EventoPlagaDetalleSerializer
        return EventoPlagaSerializer

    # Autoasignación del usuario que crea el evento
    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)


# ────────────────────────────────────────────────────────────────
# 🔮 PREDICCIÓN DE PLAGA – CONSULTA, CREACIÓN Y VALIDACIÓN MANUAL
# ────────────────────────────────────────────────────────────────
class PrediccionPlagaFilter(FilterSet):
    class Meta:
        model = PrediccionPlaga
        fields = ["tipo", "fecha_prediccion"]


class PrediccionPlagaViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin):
    """
    Vista para predicciones de plaga.
    - GET    /plagas/predicciones/        → listado
    - POST   /plagas/predicciones/        → crear predicción
    - GET    /plagas/predicciones/<pk>/   → detalle
    - POST   /plagas/predicciones/<pk>/confirmar/ → validación manual
    """
    queryset = PrediccionPlaga.objects.select_related("tipo", "lectura_climatica").all()
    permission_classes = [permissions.IsAuthenticated]

    # Filtros y ordenamiento
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = PrediccionPlagaFilter
    ordering_fields = ["fecha_prediccion", "probabilidad"]
    search_fields = ["accion_recomendada"]
    ordering = ["-fecha_prediccion"]

    # Serializador dinámico según la acción
    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return PrediccionPlagaDetalleSerializer
        return PrediccionPlagaSerializer

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        """
        POST personalizado para confirmar que una predicción fue revisada manualmente.
        Marca `generada_por_modelo = False`.
        """
        pred = self.get_object()
        pred.generada_por_modelo = False
        pred.save(update_fields=["generada_por_modelo"])
        return Response({"status": "confirmada", "id": pred.id})
