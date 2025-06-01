# control_calidad/models.py
"""
Modelo de automatización para control de calidad en lotes procesados.
Incluye:
- Cálculos automáticos de % grano sano y defectuoso
- Validación de integridad con DecimalField y rangos 0–100%
- Preparación para integración en reportes analíticos y sistemas predictivos
"""

from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# Enumeración legible para el tipo de grano procesado
class GranoTipo(models.TextChoices):
    CAFE = 'cafe', _('Café')
    MAIZ = 'maiz', _('Maíz')
    ARROZ = 'arroz', _('Arroz')
    OTRO = 'otro', _('Otro')


class LoteProcesado(models.Model):
    """
    Representa un lote de grano después de un análisis de calidad.
    Permite trazabilidad, control y optimización de procesos agroindustriales.
    """
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lotes_procesados',
        db_index=True,
        help_text=_('Usuario cliente que recibe el informe')
    )
    codigo_lote = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Identificador único de lote')
    )
    tipo_grano = models.CharField(
        max_length=20,
        choices=GranoTipo.choices,
        default=GranoTipo.OTRO,
        help_text=_('Tipo de grano procesado')
    )
    fecha_procesamiento = models.DateField(
        help_text=_('Fecha en que se procesó el lote')
    )
    cantidad_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_('Cantidad total procesada (kg)')
    )
    humedad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_('Porcentaje de humedad (%)')
    )
    impurezas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_('Porcentaje de impurezas (%)')
    )
    grano_bueno = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_('Porcentaje de grano sano (%)')
    )
    grano_defectuoso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        help_text=_('Porcentaje de grano defectuoso (%)')
    )
    observaciones = models.TextField(
        blank=True,
        help_text=_('Notas adicionales del análisis')
    )
    enviado = models.BooleanField(
        default=False,
        help_text=_('Indica si el informe ha sido entregado al cliente')
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Fecha y hora de creación del registro')
    )

    class Meta:
        verbose_name = _('Lote Procesado')
        verbose_name_plural = _('Lotes Procesados')
        ordering = ['-fecha_procesamiento', 'codigo_lote']
        indexes = [
            models.Index(fields=['cliente', 'fecha_procesamiento']),
            models.Index(fields=['codigo_lote'])
        ]

    def __str__(self):
        return f"Lote {self.codigo_lote} ({self.get_tipo_grano_display()})"

    def save(self, *args, **kwargs):
        """
        Lógica automática de cálculo:
        - Si no se define grano_defectuoso, se calcula como 100 - humedad - impurezas - bueno
        - Si no se define grano_bueno, se calcula como 100 - humedad - impurezas - defectuoso
        """
        if self.grano_defectuoso is None and self.grano_bueno is not None:
            total = sum(filter(None, [self.humedad, self.impurezas, self.grano_bueno]))
            self.grano_defectuoso = max(Decimal('0'), Decimal('100') - total)

        elif self.grano_bueno is None and self.grano_defectuoso is not None:
            total = sum(filter(None, [self.humedad, self.impurezas, self.grano_defectuoso]))
            self.grano_bueno = max(Decimal('0'), Decimal('100') - total)

        super().save(*args, **kwargs)
