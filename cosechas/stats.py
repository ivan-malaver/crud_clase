# cosechas/stats.py
"""
Vista de estadísticas y análisis estratégico para la app de cosechas.
Incluye:
- KPIs operativos: producción, rendimiento, rentabilidad
- Agregados por cultivo, usuario, unidad de medida
- Preparación de datos para gráficas
- Exportación y cálculos extendidos con Pandas
"""

import pandas as pd
from django.db.models import Avg, Sum, Count, F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cosecha

class CosechaStatsView(APIView):
    """
    GET /cosechas/stats/
    Devuelve indicadores clave para análisis gráfico y planificación agrícola.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = {}

        # ─────────────────────────────────────────────
        # 1️⃣  Estadísticas agregadas por cultivo
        # ─────────────────────────────────────────────
        cultivo_agg = Cosecha.objects.values(nombre=F("cultivo__nombre")).annotate(
            total_produccion=Sum("cantidad_obtenida"),
            promedio_rendimiento=Avg("rendimiento"),
            precio_medio=Avg("precio_venta_unitario"),
            utilidad_total=Sum("utilidad_neta_estimada"),
            costos_total=Sum("costo_total")
        )
        cultivo_df = pd.DataFrame(cultivo_agg)

        # ─────────────────────────────────────────────
        # 2️⃣  Producción total por unidad (kg, ton...)
        # ─────────────────────────────────────────────
        unidad_agg = Cosecha.objects.values("unidad").annotate(
            total=Sum("cantidad_obtenida")
        )
        unidad_df = pd.DataFrame(unidad_agg)

        # ─────────────────────────────────────────────
        # 3️⃣  Estadísticas por usuario
        # ─────────────────────────────────────────────
        usuario_agg = Cosecha.objects.values(usuario=F("registrado_por__email")).annotate(
            total_cosechas=Count("id"),
            utilidad_promedio=Avg("utilidad_neta_estimada")
        )
        usuario_df = pd.DataFrame(usuario_agg)

        # ─────────────────────────────────────────────
        # 4️⃣  Resumen general de KPIs
        # ─────────────────────────────────────────────
        globales = Cosecha.objects.aggregate(
            total_produccion=Sum("cantidad_obtenida"),
            rendimiento_medio=Avg("rendimiento"),
            precio_promedio=Avg("precio_venta_unitario"),
            utilidad_total=Sum("utilidad_neta_estimada"),
            costos_totales=Sum("costo_total")
        )

        # ─────────────────────────────────────────────
        # 5️⃣  Preparación de datos para gráficas
        # ─────────────────────────────────────────────
        graficos = {
            "barra_cultivos": {
                "labels": cultivo_df["nombre"].tolist(),
                "produccion": cultivo_df["total_produccion"].fillna(0).tolist(),
                "utilidad": cultivo_df["utilidad_total"].fillna(0).tolist(),
            },
            "pastel_unidades": {
                "labels": unidad_df["unidad"].tolist(),
                "valores": unidad_df["total"].fillna(0).tolist(),
            },
            "linea_usuarios": {
                "labels": usuario_df["usuario"].tolist(),
                "valores": usuario_df["utilidad_promedio"].fillna(0).tolist(),
            },
        }

        # ─────────────────────────────────────────────
        # 6️⃣  Construcción final del response
        # ─────────────────────────────────────────────
        datos["resumen"] = globales
        datos["por_cultivo"] = cultivo_df.to_dict(orient="records")
        datos["por_unidad"] = unidad_df.to_dict(orient="records")
        datos["por_usuario"] = usuario_df.to_dict(orient="records")
        datos["graficos"] = graficos

        return Response(datos)
