# sensores/serializers.py
"""
Serializadores robustos para los modelos IoT
Incluye:
  • Campos adicionales para automatización
  • Validación de unidad y tipo
  • Evaluación de rango activo
"""

from decimal import Decimal, InvalidOperation
from rest_framework import serializers
from .models import Sensor, Medicion, TipoSensor


# ────────────────────────────────────────────────────────────────
# 🌡️ SENSOR
# ────────────────────────────────────────────────────────────────
class SensorSerializer(serializers.ModelSerializer):
    # Campo legible del enum (solo lectura)
    tipo_label = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Sensor
        fields = (
            "id",
            "nombre",
            "tipo",
            "tipo_label",
            "ubicacion",
            "activo",
            "creado_en",
            "valor_referencia",
            "rango_minimo",
            "rango_maximo",
        )
        read_only_fields = ("id", "creado_en")


# ────────────────────────────────────────────────────────────────
# 📈 MEDICIÓN (creación / actualización)
# ────────────────────────────────────────────────────────────────
class MedicionSerializer(serializers.ModelSerializer):
    sensor = serializers.PrimaryKeyRelatedField(
        queryset=Sensor.objects.filter(activo=True)
    )

    fuera_de_rango = serializers.SerializerMethodField()

    class Meta:
        model = Medicion
        fields = ("id", "sensor", "valor", "unidad", "timestamp", "fuera_de_rango")
        read_only_fields = ("id", "timestamp", "fuera_de_rango")

    def get_fuera_de_rango(self, obj):
        """Evalúa si la medición excede los límites establecidos."""
        return obj.sensor.esta_fuera_de_rango(obj.valor)

    def validate_valor(self, value):
        """Valida que el valor sea un número positivo válido."""
        try:
            dec = value if isinstance(value, Decimal) else Decimal(str(value))
            if dec <= 0:
                raise serializers.ValidationError("El valor debe ser positivo.")
        except (InvalidOperation, TypeError):
            raise serializers.ValidationError("Formato decimal inválido.")
        return dec

    def validate(self, attrs):
        sensor: Sensor = attrs["sensor"]
        unidad = attrs["unidad"].strip().lower()

        if not sensor.activo:
            raise serializers.ValidationError("El sensor está inactivo.")

        # Validación unidad según tipo de sensor
        reglas = {
            TipoSensor.TEMPERATURA: {"°c", "c", "celsius"},
            TipoSensor.HUMEDAD: {"%", "porcentaje"},
            TipoSensor.PRESION: {"pa", "hpa", "psi"},
            TipoSensor.LUMINOSIDAD: {"lux"},
            TipoSensor.GAS: {"ppm"},
            TipoSensor.PH: {"ph"},
        }
        if unidad not in reglas.get(sensor.tipo, set()):
            raise serializers.ValidationError(
                f"La unidad «{unidad}» no coincide con un sensor de tipo {sensor.get_tipo_display()}"
            )

        # Normaliza unidad
        unidad_normalizada = {
            "°c": "°C", "c": "°C",
            "%": "%", "pa": "Pa",
            "hpa": "hPa", "psi": "psi",
            "lux": "lux", "ppm": "ppm"
        }.get(unidad, unidad)

        attrs["unidad"] = unidad_normalizada
        return attrs


# ────────────────────────────────────────────────────────────────
# 📊 MEDICIÓN DETALLE (lectura enriquecida)
# ────────────────────────────────────────────────────────────────
class MedicionDetalleSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)

    class Meta:
        model = Medicion
        fields = ("id", "sensor", "valor", "unidad", "timestamp")
        read_only_fields = ("id", "timestamp", "sensor")