# control_calidad/stats.py
"""
Módulo de estadísticas, análisis y Machine Learning para control de calidad.
Incluye:
- KPIs operativos
- Generación de reportes analíticos
- Modelos predictivos básicos
- Preparación de datos para gráficas y decisiones estratégicas
"""

import pandas as pd
from django.db.models import Avg, Count, Sum, F
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import LoteProcesado

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

class LoteCalidadStatsView(APIView):
    """
    GET /control-calidad/stats/
    Devuelve estadísticas agregadas y predicciones simples sobre lotes procesados.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Carga de datos desde el ORM
        lotes = LoteProcesado.objects.select_related("cliente")
        df = pd.DataFrame.from_records(lotes.values(
            "tipo_grano", "cantidad_kg", "humedad", "impurezas",
            "grano_bueno", "grano_defectuoso", "cliente__email"
        ))

        # Limpieza y preparación básica
        df = df.dropna()
        df["cliente"] = df.pop("cliente__email")

        # KPIs generales
        kpis = df.groupby("tipo_grano").agg({
            "cantidad_kg": "sum",
            "grano_bueno": "mean",
            "grano_defectuoso": "mean",
            "humedad": "mean",
            "impurezas": "mean"
        }).reset_index()

        # Visualización por cliente
        clientes = df.groupby("cliente").agg({
            "cantidad_kg": "sum",
            "grano_defectuoso": "mean",
            "grano_bueno": "mean"
        }).reset_index()

        # Modelado predictivo: predicción del grano sano
        X = df[["cantidad_kg", "humedad", "impurezas"]]
        y = df["grano_bueno"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        modelo = LinearRegression()
        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)
        error = mean_squared_error(y_test, y_pred, squared=False)  # RMSE

        # Reporte generado
        reporte = {
            "kpis_por_tipo_grano": kpis.to_dict(orient="records"),
            "resumen_por_cliente": clientes.to_dict(orient="records"),
            "modelo_predictivo": {
                "descripcion": "Regresión lineal para predecir % grano sano",
                "error_rmse": round(error, 2),
                "coeficientes": dict(zip(X.columns, modelo.coef_.round(2))),
            }
        }

        return Response(reporte)
