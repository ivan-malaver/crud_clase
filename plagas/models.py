# plagas/models.py
"""
Modelos mejorados para la gestión y predicción de plagas.
Incluyen validaciones, enums legibles y preparación para automatización agrícola.
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from clima.models import LecturaClima  # ← asegura que la app clima esté disponible


# ────────────────────────────────────────────────────────────────
# 🌿 TIPO DE PLAGA
# ────────────────────────────────────────────────────────────────
class TipoPlaga(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Temporada(models.TextChoices):
        PRIMAVERA = "primavera", _("Primavera")
        VERANO = "verano", _("Verano")
        OTONO = "otono", _("Otoño")
        INVIERNO = "invierno", _("Invierno")
        TODO_ANO = "todo_ano", _("Todo el año")

    temporada = models.CharField(
        max_length=20,
        choices=Temporada.choices,
        default=Temporada.TODO_ANO,
    )
    cultivo_afectado = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Tipo de plaga"
        verbose_name_plural = "Tipos de plaga"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ────────────────────────────────────────────────────────────────
# 🐛 EVENTO DE PLAGA DETECTADO
# ────────────────────────────────────────────────────────────────
class EventoPlaga(models.Model):
    class Severidad(models.TextChoices):
        LEVE = "leve", _("Leve")
        MODERADA = "moderada", _("Moderada")
        SEVERA = "severa", _("Severa")

    tipo = models.ForeignKey(
        TipoPlaga,
        related_name="eventos",
        on_delete=models.CASCADE
    )
    fecha_detectada = models.DateField()
    ubicacion = models.CharField(max_length=200)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    severidad = models.CharField(
        max_length=10,
        choices=Severidad.choices
    )
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = "Evento de plaga"
        verbose_name_plural = "Eventos de plaga"
        ordering = ["-fecha_detectada"]
        indexes = [
            models.Index(fields=["tipo", "fecha_detectada"]),
        ]

    def __str__(self):
        return f"{self.tipo.nombre} en {self.ubicacion} ({self.fecha_detectada})"


# ────────────────────────────────────────────────────────────────
# 🔮 PREDICCIÓN DE PLAGA AUTOMATIZADA
# ────────────────────────────────────────────────────────────────
class PrediccionPlaga(models.Model):
    tipo = models.ForeignKey(
        TipoPlaga,
        related_name="predicciones",
        on_delete=models.CASCADE
    )
    fecha_prediccion = models.DateField(auto_now_add=True)
    lectura_climatica = models.ForeignKey(
        LecturaClima,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    probabilidad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Porcentaje de riesgo entre 0 y 100"),
    )
    accion_recomendada = models.TextField(
        help_text=_("Ej: Aplicar pesticida, monitorear área, etc.")
    )
    generada_por_modelo = models.BooleanField(
        default=True,
        help_text=_("Si fue generada automáticamente por el modelo de IA.")
    )

    class Meta:
        verbose_name = "Predicción de plaga"
        verbose_name_plural = "Predicciones de plaga"
        ordering = ["-fecha_prediccion"]
        indexes = [
            models.Index(fields=["tipo", "fecha_prediccion"]),
        ]

    def clean(self):
        """
        Valida que la probabilidad esté dentro del rango permitido (0-100).
        """
        if self.probabilidad is not None and not (Decimal("0") <= self.probabilidad <= Decimal("100")):
            raise ValidationError({"probabilidad": _("Debe estar entre 0 y 100")})

    def __str__(self):
        return f"Predicción {self.tipo.nombre} ({self.probabilidad}%)"
