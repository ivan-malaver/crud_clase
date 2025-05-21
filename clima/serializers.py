# clima/serializers.py
"""
Serializadores para sensores climáticos y sus lecturas.
Incluye:
- Validaciones personalizadas
- Versión enriquecida para vistas detalladas
- Alineación con estrategias de automatización agrícola
"""

from rest_framework import serializers
from .models import DispositivoClima, LecturaClima


class DispositivoClimaSerializer(serializers.ModelSerializer):
    """
    Serializa un DispositivoClima (sensor o estación).
    Valida el tipo (interno/externo) y estructura campos clave.
    """

    class Meta:
        model = DispositivoClima
        fields = ['id', 'nombre', 'tipo', 'ubicacion', 'activo', 'creado_en']

    def validate_tipo(self, value):
        if value not in ['interno', 'externo']:
            raise serializers.ValidationError("El tipo debe ser 'interno' o 'externo'.")
        return value


class LecturaClimaSerializer(serializers.ModelSerializer):
    """
    Serializa una lectura tomada por un sensor climático.
    Incluye validación de temperatura.
    """

    class Meta:
        model = LecturaClima
        fields = [
            'id', 'dispositivo', 'temperatura', 'humedad', 'presion',
            'viento', 'precipitacion', 'radiacion_solar', 'timestamp'
        ]

    def validate_temperatura(self, value):
        if value is not None and (value < -100 or value > 100):
            raise serializers.ValidationError("La temperatura debe estar entre -100°C y 100°C.")
        return value


class LecturaClimaDetalleSerializer(serializers.ModelSerializer):
    """
    Versión extendida del serializador para vistas detalladas.
    Incluye datos completos del dispositivo que tomó la lectura.
    """
    dispositivo = DispositivoClimaSerializer(read_only=True)

    class Meta:
        model = LecturaClima
        fields = [
            'id', 'dispositivo', 'temperatura', 'humedad', 'presion',
            'viento', 'precipitacion', 'radiacion_solar', 'timestamp'
        ]
