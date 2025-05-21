from django.urls import path
from .views import (
    TipoPlagaViewSet,
    EventoPlagaViewSet,
    PrediccionPlagaViewSet,
)
from .stats import PlagasStatsView

# Asignamos manualmente las vistas usando `.as_view()` con sus métodos
tipo_plaga_list     = TipoPlagaViewSet.as_view({'get': 'list', 'post': 'create'})
tipo_plaga_detail   = TipoPlagaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

evento_plaga_list   = EventoPlagaViewSet.as_view({'get': 'list', 'post': 'create'})
evento_plaga_detail = EventoPlagaViewSet.as_view({'get': 'retrieve'})

prediccion_list     = PrediccionPlagaViewSet.as_view({'get': 'list', 'post': 'create'})
prediccion_detail   = PrediccionPlagaViewSet.as_view({'get': 'retrieve'})
prediccion_confirm  = PrediccionPlagaViewSet.as_view({'post': 'confirmar'})

urlpatterns = [
    # 🌿 Tipos de plaga
    path("tipos-plaga/", tipo_plaga_list, name="tipo-plaga-list"),
    path("tipos-plaga/<int:pk>/", tipo_plaga_detail, name="tipo-plaga-detail"),

    # 🐛 Eventos de plaga
    path("eventos-plaga/", evento_plaga_list, name="evento-plaga-list"),
    path("eventos-plaga/<int:pk>/", evento_plaga_detail, name="evento-plaga-detail"),

    # 🔮 Predicciones de plaga
    path("predicciones-plaga/", prediccion_list, name="prediccion-plaga-list"),
    path("predicciones-plaga/<int:pk>/", prediccion_detail, name="prediccion-plaga-detail"),
    path("predicciones-plaga/<int:pk>/confirmar/", prediccion_confirm, name="prediccion-confirmar"),

    # 📊 Estadísticas
    path("stats/", PlagasStatsView.as_view(), name="plagas-stats"),
]
