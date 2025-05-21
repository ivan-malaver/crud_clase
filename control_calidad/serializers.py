# control_calidad/serializers.py
"""
Serializador para LoteProcesado (control de calidad).
Mejoras implementadas:
- Validaciones automáticas de porcentaje
- Conversión limpia de códigos de lote
- Visualización enriquecida para UI (etiquetas y nombres)
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import LoteProcesado

User = get_user_model()


class LoteProcesadoSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo LoteProcesado:
    - Usado para crear, actualizar y mostrar datos analíticos del control de calidad
    - Aplica validaciones lógicas y formatea campos legibles para UI
    """
    cliente = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="ID del cliente que recibe el informe"
    )
    cliente_nombre = serializers.CharField(
        source="cliente.get_full_name", read_only=True,
        help_text="Nombre completo del cliente"
    )
    tipo_grano_label = serializers.CharField(
        source="get_tipo_grano_display", read_only=True,
        help_text="Tipo de grano legible"
    )

    class Meta:
        model = LoteProcesado
        fields = [
            "id", "cliente", "cliente_nombre",
            "codigo_lote", "tipo_grano", "tipo_grano_label",
            "fecha_procesamiento", "cantidad_kg",
            "humedad", "impurezas", "grano_bueno", "grano_defectuoso",
            "observaciones", "enviado", "creado_en"
        ]
        read_only_fields = [
            "id", "cliente_nombre", "tipo_grano_label", "enviado", "creado_en"
        ]

    def validate_codigo_lote(self, value):
        """
        Normaliza el código de lote eliminando espacios y pasando a mayúscula.
        """
        return value.strip().upper()

    def validate(self, data):
        """
        Validación cruzada:
        - Si humedad + impurezas + grano_bueno + grano_defectuoso > 100%, se lanza error
        - Esto evita valores físicamente imposibles
        """
        h = data.get("humedad", getattr(self.instance, "humedad", None))
        i = data.get("impurezas", getattr(self.instance, "impurezas", None))
        b = data.get("grano_bueno", getattr(self.instance, "grano_bueno", None))
        d = data.get("grano_defectuoso", getattr(self.instance, "grano_defectuoso", None))

        if None not in (h, i, b, d):
            total = h + i + b + d
            if total > Decimal("100"):
                raise serializers.ValidationError(
                    "La suma de porcentajes no puede exceder 100%."
                )

        return data
