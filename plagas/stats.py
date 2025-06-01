# plagas/stats.py
"""
Vista analítica para eventos y predicciones de plagas.
Incluye indicadores clave y gráficos de apoyo para tomar decisiones
basadas en datos históricos y recientes.
"""

from django.db.models import Count, Avg, Max, Min
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EventoPlaga, PrediccionPlaga, TipoPlaga

class PlagasStatsView(APIView):
    """
    GET /plagas/stats/
    Devuelve:
    - Total de eventos por tipo
    - Eventos por severidad
    - Promedio y máximos de probabilidad en predicciones
    - Sugerencias visuales para gráficos de barra y pastel
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Conteo por tipo
        tipos = TipoPlaga.objects.all()
        eventos_por_tipo = [
            {"tipo": t.nombre, "eventos": t.eventos.count()}
            for t in tipos
        ]

        # Eventos por severidad
        severidad = EventoPlaga.objects.values("severidad").annotate(total=Count("id"))

        # Métricas de predicción
        pred_stats = PrediccionPlaga.objects.aggregate(
            total=Count("id"),
            promedio=Avg("probabilidad"),
            maxima=Max("probabilidad"),
            minima=Min("probabilidad")
        )

        return Response({
            "eventos_por_tipo": eventos_por_tipo,
            "eventos_por_severidad": list(severidad),
            "predicciones": pred_stats,
            "graficos": {
                "barra_eventos": [e["eventos"] for e in eventos_por_tipo],
                "etiquetas_eventos": [e["tipo"] for e in eventos_por_tipo],
                "pastel_severidad": {s["severidad"]: s["total"] for s in severidad},
            }
        })
