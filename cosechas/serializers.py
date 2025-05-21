# cosechas/serializers.py
"""
Serializadores para los modelos de Cultivo y Cosecha.
• Incluye lógica de cálculo de rendimiento en validación
• Detalle enriquecido con relaciones anidadas (usuario, clima, cultivo)
• Ampliado con campos económicos (costos, precios, utilidad)
"""

from rest_framework import serializers
from .models import Cultivo, Cosecha
from clima.serializers import LecturaClimaSerializer
from usuarios.serializers import UsuarioSerializer


class CultivoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Cultivo (catálogo de productos).
    """
    class Meta:
        model = Cultivo
        fields = ["id", "nombre", "descripcion", "ciclo"]
        read_only_fields = ["id"]


class CosechaSerializer(serializers.ModelSerializer):
    """
    Serializador base para crear y editar cosechas.
    Calcula el rendimiento si no se proporciona y permite
    gestionar los costos y ganancias proyectadas.
    """
    class Meta:
        model = Cosecha
        fields = [
            "id", "cultivo", "parcela", "superficie_ha",
            "fecha_siembra", "fecha_inicio_cosecha", "fecha_fin_cosecha",
            "cantidad_obtenida", "unidad", "rendimiento",
            "clima_inicio", "clima_fin",
            "fertilizante_usado", "cantidad_fertilizante",
            "pesticida_usado", "cantidad_pesticida",
            "agua_utilizada_m3", "costo_semilla", "costo_fertilizante",
            "costo_pesticida", "costo_mano_obra", "costo_riego", "otros_costos",
            "costo_total", "precio_venta_unitario", "ingreso_total_estimado",
            "margen_utilidad_esperado", "utilidad_neta_estimada",
            "registrado_por", "notas", "creado_en"
        ]
        read_only_fields = [
            "id", "rendimiento", "costo_total",
            "ingreso_total_estimado", "utilidad_neta_estimada", "creado_en"
        ]

    def _calcular_rendimiento(self, superficie, cantidad):
        if superficie and cantidad:
            return round(cantidad / superficie, 2)
        return None

    def validate(self, data):
        superficie = data.get("superficie_ha")
        cantidad = data.get("cantidad_obtenida")
        if superficie and cantidad:
            data["rendimiento"] = self._calcular_rendimiento(superficie, cantidad)
        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        superficie = validated_data.get("superficie_ha", instance.superficie_ha)
        cantidad = validated_data.get("cantidad_obtenida", instance.cantidad_obtenida)
        validated_data["rendimiento"] = self._calcular_rendimiento(superficie, cantidad)
        return super().update(instance, validated_data)


class CosechaDetalleSerializer(serializers.ModelSerializer):
    """
    Vista enriquecida de una cosecha para detalle.
    Anida: Cultivo, Clima (inicio y fin), Usuario
    """
    cultivo = CultivoSerializer(read_only=True)
    clima_inicio = LecturaClimaSerializer(read_only=True)
    clima_fin = LecturaClimaSerializer(read_only=True)
    registrado_por = UsuarioSerializer(read_only=True)

    class Meta:
        model = Cosecha
        fields = [
            "id", "cultivo", "parcela", "superficie_ha",
            "fecha_siembra", "fecha_inicio_cosecha", "fecha_fin_cosecha",
            "cantidad_obtenida", "unidad", "rendimiento",
            "clima_inicio", "clima_fin",
            "fertilizante_usado", "cantidad_fertilizante",
            "pesticida_usado", "cantidad_pesticida",
            "agua_utilizada_m3", "costo_semilla", "costo_fertilizante",
            "costo_pesticida", "costo_mano_obra", "costo_riego", "otros_costos",
            "costo_total", "precio_venta_unitario", "ingreso_total_estimado",
            "margen_utilidad_esperado", "utilidad_neta_estimada",
            "registrado_por", "notas", "creado_en"
        ]
        read_only_fields = fields
