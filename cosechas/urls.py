"""
Rutas RESTful para el módulo de Cosechas 🌱

Incluye:
- Endpoints funcionales para gestión de cultivos y cosechas.
- Ruta adicional para estadísticas analíticas (para gráficos e informes).
- Soporte para sufijos opcionales: .json, .api, etc. (DRF).
"""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

# Vistas funcionales de cultivos y cosechas
from .views import (
    listar_cultivos,        # GET  → Listar cultivos
    registrar_cultivo,      # POST → Crear nuevo cultivo
    listar_cosechas,        # GET  → Listar cosechas
    registrar_cosecha,      # POST → Registrar cosecha
    detalle_cosecha,        # GET  → Detalle de cosecha
    actualizar_cosecha,     # PUT/PATCH → Editar cosecha
    eliminar_cosecha        # DELETE → Eliminar cosecha
)

# Vista adicional para analítica de datos
from .stats import CosechaStatsView  # GET → Estadísticas de cosechas

# Definición de rutas REST
urlpatterns = [

    # ───── 🌾 CULTIVOS ─────
    path("cultivos/", listar_cultivos, name="cultivo-list"),
    path("cultivos/registrar/", registrar_cultivo, name="cultivo-create"),

    # ───── 🚜 COSECHAS ─────
    path("cosechas/", listar_cosechas, name="cosecha-list"),
    path("cosechas/registrar/", registrar_cosecha, name="cosecha-create"),
    path("cosechas/<int:pk>/", detalle_cosecha, name="cosecha-detail"),
    path("cosechas/<int:pk>/editar/", actualizar_cosecha, name="cosecha-update"),
    path("cosechas/<int:pk>/eliminar/", eliminar_cosecha, name="cosecha-delete"),

    # ───── 📊 ESTADÍSTICAS ─────
    path("cosechas/stats/", CosechaStatsView.as_view(), name="cosecha-stats"),
]

# Permitir sufijos como .json, .csv, etc.
urlpatterns = format_suffix_patterns(urlpatterns)
