# plagas/serializers.py
"""
Serializadores DRF para modelos del módulo de plagas
Incluyen:
- Etiquetas legibles para enums
- Validaciones reforzadas
- Serializadores anidados solo en vistas de detalle
- Estructura clara entre POST/PUT vs GET enriquecido
"""

from rest_framework import serializers
from decimal import Decimal, InvalidOperation
from .models import TipoPlaga, EventoPlaga, PrediccionPlaga
from clima.serializers import LecturaClimaSerializer


# ────────────────────────────────────────────────────────────────
# 🌿 TIPO DE PLAGA
# ────────────────────────────────────────────────────────────────
class TipoPlagaSerializer(serializers.ModelSerializer):
    temporada_label = serializers.CharField(
        source="get_temporada_display", read_only=True
    )

    class Meta:
        model = TipoPlaga
        fields = (
            "id",
            "nombre",
            "descripcion",
            "cultivo_afectado",
            "temporada",
            "temporada_label",
        )
        read_only_fields = ("id",)


# ────────────────────────────────────────────────────────────────
# 🐛 EVENTO DE PLAGA
# ────────────────────────────────────────────────────────────────
class EventoPlagaSerializer(serializers.ModelSerializer):
    """
    Serializador básico para crear o editar eventos (POST / PUT / PATCH)
    Envía id de tipo de plaga y usuario responsable
    """
    class Meta:
        model = EventoPlaga
        fields = (
            "id",
            "tipo",
            "fecha_detectada",
            "ubicacion",
            "registrado_por",
            "severidad",
            "observaciones",
        )
        read_only_fields = ("id",)


class EventoPlagaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador extendido de solo lectura para detalle (GET)
    Muestra tipo de plaga y usuario con objetos anidados o representaciones legibles
    """
    tipo = TipoPlagaSerializer(read_only=True)
    registrado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventoPlaga
        fields = (
            "id",
            "tipo",
            "fecha_detectada",
            "ubicacion",
            "registrado_por",
            "severidad",
            "observaciones",
        )
        read_only_fields = fields


# ────────────────────────────────────────────────────────────────
# 🔮 PREDICCIÓN DE PLAGA
# ────────────────────────────────────────────────────────────────
class PrediccionPlagaSerializer(serializers.ModelSerializer):
    """
    Serializador para crear predicciones (POST) o actualizarlas (PUT/PATCH)
    Valida que la probabilidad esté en rango 0–100
    """
    class Meta:
        model = PrediccionPlaga
        fields = (
            "id",
            "tipo",
            "fecha_prediccion",
            "lectura_climatica",
            "probabilidad",
            "accion_recomendada",
            "generada_por_modelo",
        )
        read_only_fields = ("id", "fecha_prediccion")

    def validate_probabilidad(self, value):
        """Valida que la probabilidad sea un decimal válido entre 0 y 100"""
        try:
            dec = value if isinstance(value, Decimal) else Decimal(str(value))
        except InvalidOperation:
            raise serializers.ValidationError("Formato decimal inválido.")
        if not (Decimal("0") <= dec <= Decimal("100")):
            raise serializers.ValidationError("Probabilidad debe estar entre 0 y 100.")
        return dec


class PrediccionPlagaDetalleSerializer(serializers.ModelSerializer):
    """
    Serializador extendido para visualizar predicciones completas (GET)
    Incluye datos anidados de clima y tipo de plaga
    """
    tipo = TipoPlagaSerializer(read_only=True)
    lectura_climatica = LecturaClimaSerializer(read_only=True)

    class Meta:
        model = PrediccionPlaga
        fields = (
            "id",
            "tipo",
            "fecha_prediccion",
            "lectura_climatica",
            "probabilidad",
            "accion_recomendada",
            "generada_por_modelo",
        )
        read_only_fields = fields
