# cosechas/models.py
"""
Modelos para la gestión de cultivos y cosechas
──────────────────────────────────────────────────────────
• 100 % compatibles con AUTH_USER_MODEL (evita dependencias rígidas)
• `DecimalField` para cantidades ⇒ precisión financiera/agrícola
• Índices y ordenamiento  ─  analítica más veloz
• Cálculo automático de rendimiento en `save()` + método explícito
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


# ╭──────────────────────────────────────────────────────────────╮
# │ 🌱  CULTIVO                                                 │
# ╰──────────────────────────────────────────────────────────────╯
class Cultivo(models.Model):
    """Catálogo maestro de cultivos (maíz, trigo, café, etc.)."""
    nombre        = models.CharField(max_length=100, unique=True)
    descripcion   = models.TextField(blank=True)
    ciclo         = models.CharField(
        max_length=50,
        help_text="Ej.: anual, bianual, permanente",
    )

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"

    def __str__(self) -> str:
        return self.nombre


# ╭──────────────────────────────────────────────────────────────╮
# │ 🚜  COSECHA                                                 │
# ╰──────────────────────────────────────────────────────────────╯
class Cosecha(models.Model):
    """Registro operativo y productivo de una cosecha concreta."""

    # --- Relaciones clave -------------------------------------
    cultivo         = models.ForeignKey(
        Cultivo,
        related_name="cosechas",
        on_delete=models.CASCADE,
    )
    registrado_por  = models.ForeignKey(                     # trazabilidad
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    # --- Identificación de lote --------------------------------
    parcela         = models.CharField(max_length=100, help_text="Lote agrícola")
    superficie_ha   = models.DecimalField(
        max_digits=8, decimal_places=2,                      # hasta 999 999,99 ha
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Superficie sembrada (ha)",
    )

    # --- Fechas clave ------------------------------------------
    fecha_siembra          = models.DateField()
    fecha_inicio_cosecha   = models.DateField()
    fecha_fin_cosecha      = models.DateField()

    # --- Producción y rendimiento ------------------------------
    cantidad_obtenida = models.DecimalField(
        max_digits=12, decimal_places=2,                     # hasta 999 999 999,99 kg
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Producción total",
    )
    unidad            = models.CharField(max_length=10, help_text="kg, ton, etc.")
    rendimiento       = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        editable=False,                                      # autocalculado
        help_text="Producción / ha",
    )

    # --- Condiciones climáticas (opcional) ---------------------
    clima_inicio = models.ForeignKey(
        "clima.LecturaClima",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="cosechas_inicio",
    )
    clima_fin    = models.ForeignKey(
        "clima.LecturaClima",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="cosechas_fin",
    )

    # --- Insumos -----------------------------------------------
    fertilizante_usado     = models.CharField(max_length=100, blank=True)
    cantidad_fertilizante  = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    pesticida_usado        = models.CharField(max_length=100, blank=True)
    cantidad_pesticida     = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)

    agua_utilizada_m3      = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text="Volumen total de agua (m³)",
    )

    # --- Metadatos ---------------------------------------------
    notas       = models.TextField(blank=True)
    creado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_fin_cosecha"]
        indexes  = [
            models.Index(fields=["cultivo", "fecha_fin_cosecha"]),
            models.Index(fields=["parcela"]),
        ]
        verbose_name = "Cosecha"
        verbose_name_plural = "Cosechas"

    # ---------- Representación legible ----------
    def __str__(self) -> str:
        return f"{self.cultivo.nombre} · {self.parcela} ({self.fecha_fin_cosecha})"

    # ---------- Lógica de negocio ---------------
    def _calcular_rendimiento(self) -> Decimal | None:
        if self.superficie_ha and self.cantidad_obtenida:
            return (self.cantidad_obtenida / self.superficie_ha).quantize(Decimal("0.01"))
        return None

    def save(self, *args, **kwargs):
        # Calcula rendimiento si no está informado
        if self.rendimiento is None:
            self.rendimiento = self._calcular_rendimiento()
        super().save(*args, **kwargs)
