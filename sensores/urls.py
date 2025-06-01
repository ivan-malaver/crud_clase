"""
Rutas REST para la app de sensores.
Incluye:
- CRUD de sensores
- Activación/desactivación de sensores
- Registro y consulta de mediciones
- Estadísticas agregadas para el frontend
- Vista HTML del panel de sensores
"""

from django.urls import path
from .views import (
    SensorListCreateView,     # Lista y crea sensores (API)
    SensorDetailView,         # Detalle, actualización y eliminación (API)
    SensorToggleActivoView,   # Activa/desactiva un sensor (API)
    MedicionListCreateView,   # Lista y crea mediciones (API)
    MedicionDetailView,       # Detalle, actualización y eliminación (API)
    SensorTemplateView        # Vista para desplegar la plantilla HTML
)
from .stats import SensorStatsView  # Vista analítica para frontend

# No se usa `app_name` porque se evitó el uso de `namespace` en las URLs

urlpatterns = [
    # 🌡️ CRUD de sensores (API REST)
    path("sensores/", SensorListCreateView.as_view(), name="sensor-list"),
    path("sensores/<int:pk>/", SensorDetailView.as_view(), name="sensor-detail"),
    path("sensores/<int:pk>/toggle/", SensorToggleActivoView.as_view(), name="sensor-toggle"),

    # 📈 Estadísticas para frontend (API REST)
    path("sensores/stats/", SensorStatsView.as_view(), name="sensor-stats"),

    # 📊 CRUD de mediciones (API REST)
    path("mediciones/", MedicionListCreateView.as_view(), name="medicion-list"),
    path("mediciones/<int:pk>/", MedicionDetailView.as_view(), name="medicion-detail"),

    # 🖥️ Vista HTML del panel de sensores (template frontend)
    path("panel/", SensorTemplateView.as_view(), name="sensor-panel"),
]
