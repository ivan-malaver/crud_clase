# clima/stats.py
"""
Módulo de análisis y machine learning para lecturas climáticas.
Incluye:
- Análisis por dispositivo y variable
- Modelado predictivo de temperatura
- Preparación para visualización y alertas
"""

import pandas as pd
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from clima.models import LecturaClima  # ← import corregido (ruta absoluta)

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error


class ClimaStatsView(APIView):
    """
    GET /clima/stats/
    Devuelve estadísticas agregadas y modelo predictivo para clima.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Cargar y preparar los datos
        qs = LecturaClima.objects.select_related("dispositivo").values(
            nombre=F("dispositivo__nombre"),
            tipo=F("dispositivo__tipo"),
            temperatura=F("temperatura"),
            humedad=F("humedad"),
            presion=F("presion"),
            viento=F("viento"),
            radiacion=F("radiacion_solar")
        )
        df = pd.DataFrame.from_records(qs).dropna()

        # KPIs promedio por tipo de dispositivo
        resumen = df.groupby("tipo").agg({
            "temperatura": "mean",
            "humedad": "mean",
            "presion": "mean",
            "viento": "mean",
            "radiacion": "mean"
        }).round(2).reset_index()

        # Modelo ML: predecir temperatura a partir de otras variables
        X = df[["humedad", "presion", "viento", "radiacion"]]
        y = df["temperatura"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = LinearRegression()
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        rmse = round(mean_squared_error(y_test, pred, squared=False), 2)

        return Response({
            "resumen_por_tipo": resumen.to_dict(orient="records"),
            "modelo_predictivo": {
                "objetivo": "Predecir temperatura en función de humedad, presión, viento y radiación solar.",
                "coeficientes": dict(zip(X.columns, model.coef_.round(2))),
                "error_rmse": rmse
            }
        })
