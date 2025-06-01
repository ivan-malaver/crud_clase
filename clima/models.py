# clima/models.py
"""
Modelos para monitoreo climático automatizado.
Incluye:
- Dispositivo de clima (estación interna/externa)
- Lectura climática multivariable
- Preparado para expansión analítica y control de invernaderos
"""

from django.db import models

class DispositivoClima(models.Model):
    """
    Estación meteorológica o sensor climático conectado.
    Puede estar en exteriores o interiores.
    """
    TIPO_CHOICES = (
        ('externo', 'Externo'),
        ('interno', 'Interno'),
    )

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    ubicacion = models.CharField(max_length=200, help_text="Ej: Zona norte del invernadero")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Dispositivo climático"
        verbose_name_plural = "Dispositivos climáticos"

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class LecturaClima(models.Model):
    """
    Registro automático de condiciones ambientales por un dispositivo climático.
    Las lecturas pueden ser en tiempo real o históricas.
    """
    dispositivo = models.ForeignKey(
        DispositivoClima,
        on_delete=models.CASCADE,
        related_name='lecturas'
    )

    # Variables climáticas registradas
    temperatura = models.FloatField(help_text="°C", null=True, blank=True)
    humedad = models.FloatField(help_text="%", null=True, blank=True)
    presion = models.FloatField(help_text="hPa", null=True, blank=True)
    viento = models.FloatField(help_text="km/h", null=True, blank=True)
    precipitacion = models.FloatField(help_text="mm", null=True, blank=True)
    radiacion_solar = models.FloatField(help_text="W/m²", null=True, blank=True)

    # Marca temporal
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Lectura climática"
        verbose_name_plural = "Lecturas climáticas"
        indexes = [
            models.Index(fields=["dispositivo", "timestamp"]),
        ]

    def __str__(self):
        return f"Lectura de {self.dispositivo.nombre} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
