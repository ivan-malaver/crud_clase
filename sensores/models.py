# sensores/models.py
"""
Modelos robustos para el módulo de sensores y mediciones con soporte para automatización.
Incluyen:
- Enum tipado para tipos de sensor
- Parámetros de activación y desactivación
- Precisión decimal para lecturas
- Protección de integridad para mediciones
- Indexación para búsquedas eficientes
"""

from decimal import Decimal
from django.db import models
from django.utils import timezone

# ────────────────────────────────────────────────────────────────
# 🔄 TIPOS DE SENSOR COMO ENUM (TextChoices)
# ────────────────────────────────────────────────────────────────
class TipoSensor(models.TextChoices):
    """
    Enumeración legible que clasifica los tipos de sensores.
    Mejora la validación y autocompletado.
    """
    TEMPERATURA = "temperatura", "Temperatura"
    HUMEDAD     = "humedad", "Humedad"
    PRESION     = "presion", "Presión"
    LUMINOSIDAD = "luminosidad", "Luminosidad"
    GAS         = "gas", "Gas"
    PH          = "ph", "pH"


# ────────────────────────────────────────────────────────────────
# 📡 MODELO SENSOR
# ────────────────────────────────────────────────────────────────
class Sensor(models.Model):
    """
    Representa un dispositivo que registra datos del ambiente o del cultivo.
    Asociado con múltiples mediciones históricas.
    También incluye parámetros de activación y referencia para automatización.
    """
    nombre = models.CharField(
        "Nombre identificador",
        max_length=100,
        unique=True,
        help_text="Ej: Sensor Temperatura Invernadero"
    )
    tipo = models.CharField(
        "Tipo de sensor",
        max_length=20,
        choices=TipoSensor.choices
    )
    ubicacion = models.CharField(
        "Ubicación física/descriptiva",
        max_length=200,
        blank=True
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el sensor sigue activo en el sistema."
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en que se registró el sensor."
    )

    # ─────────────────────────────────────────────────────────────
    # 🔧 PARÁMETROS DE AUTOMATIZACIÓN
    # ─────────────────────────────────────────────────────────────
    valor_referencia = models.DecimalField(
        "Valor objetivo",
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Valor deseado de operación automática. Ej: 25.0 °C"
    )
    rango_minimo = models.DecimalField(
        "Límite mínimo",
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Valor mínimo aceptable antes de activar el actuador."
    )
    rango_maximo = models.DecimalField(
        "Límite máximo",
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Valor máximo aceptable antes de desactivar el actuador."
    )

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensores"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    def esta_fuera_de_rango(self, valor):
        """
        Evalúa si un valor de medición está fuera de los límites definidos.
        Devuelve True si el valor está fuera del rango operativo.
        """
        if self.rango_minimo is not None and valor < self.rango_minimo:
            return True
        if self.rango_maximo is not None and valor > self.rango_maximo:
            return True
        return False


# ────────────────────────────────────────────────────────────────
# 📈 MODELO MEDICIÓN
# ────────────────────────────────────────────────────────────────
class Medicion(models.Model):
    """
    Registro individual de un valor medido por un sensor.
    Incluye validación de precisión y unidad, y mantiene historial.
    """
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.PROTECT,
        related_name="mediciones",
        help_text="Sensor asociado a la medición."
    )
    valor = models.DecimalField(
        "Valor",
        max_digits=8,
        decimal_places=3,
        help_text="Valor medido. Solo positivos."
    )
    unidad = models.CharField(
        "Unidad de medida",
        max_length=20,
        help_text="Ej: °C, %, Pa, lux"
    )
    timestamp = models.DateTimeField(
        "Fecha/hora de lectura",
        default=timezone.now,
        editable=False,
        help_text="Fecha y hora exacta de la medición."
    )

    class Meta:
        verbose_name = "Medición"
        verbose_name_plural = "Mediciones"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["sensor", "timestamp"])
        ]

    def __str__(self):
        return f"{self.sensor.nombre} | {self.valor} {self.unidad} @ {self.timestamp:%Y-%m-%d %H:%M}"

    def save(self, *args, **kwargs):
        """
        Validación adicional antes de guardar:
        - Asegura que el valor sea positivo.
        - Se puede usar self.sensor.esta_fuera_de_rango(self.valor)
          para activar lógica de alertas o actuadores.
        """
        if self.valor <= 0:
            raise ValueError("El valor de la medición debe ser positivo.")
        super().save(*args, **kwargs)
