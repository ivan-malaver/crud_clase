"""
Rutas RESTful para dispositivos y lecturas climáticas.
Incluye:
- CRUD de sensores y datos climáticos
- Endpoints separados por acción
- Preparado para integración con estadísticas
"""

from django.urls import path
from . import views
from .stats import ClimaStatsView
from rest_framework.urlpatterns import format_suffix_patterns  # Para permitir .json, .api, etc.

# ✅ Importante: NO usamos namespace si no se referencian con 'clima:...'
# Por lo tanto, removemos app_name para evitar errores de reversa si no lo estás usando así
# app_name = "clima"

urlpatterns = [
    # 🌡️ Dispositivos Climáticos (CRUD)
    path("dispositivos/", views.listar_dispositivos, name="dispositivo-list"),
    path("dispositivos/registrar/", views.registrar_dispositivo, name="dispositivo-create"),
    path("dispositivos/<int:pk>/", views.detalle_dispositivo, name="dispositivo-detail"),
    path("dispositivos/<int:pk>/editar/", views.actualizar_dispositivo, name="dispositivo-update"),
    path("dispositivos/<int:pk>/eliminar/", views.eliminar_dispositivo, name="dispositivo-delete"),

    # ☁️ Lecturas Climáticas (CRUD)
    path("lecturas/", views.listar_lecturas, name="lectura-list"),  # 💥 Ruta usada en la plantilla: {% url 'lectura-list' %}
    path("lecturas/registrar/", views.registrar_lectura, name="lectura-create"),
    path("lecturas/<int:pk>/", views.detalle_lectura, name="lectura-detail"),
    path("lecturas/<int:pk>/editar/", views.actualizar_lectura, name="lectura-update"),
    path("lecturas/<int:pk>/eliminar/", views.eliminar_lectura, name="lectura-delete"),

    # 📊 Estadísticas climáticas para dashboard
    path("stats/", ClimaStatsView.as_view(), name="clima-stats"),
]

# Permite rutas como /lecturas.json o /dispositivos.api si se desea
urlpatterns = format_suffix_patterns(urlpatterns)
