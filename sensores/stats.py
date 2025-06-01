# sensores/stats.py
"""
Vista estadística para sensores y sus mediciones.
Incluye:
- Conteo y estado de sensores
- Rango de operación vs valores actuales
- Uso de actuadores (virtuales)
- Preparación para gráficas en el frontend
"""

from django.db.models import Count, Max, Min, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Sensor, Medicion

class SensorStatsView(APIView):
    """
    GET /api/sensores/stats/
    Devuelve datos estadísticos para graficar en frontend.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sensores = Sensor.objects.all()
        datos = []

        for sensor in sensores:
            mediciones = sensor.mediciones.all()
            total = mediciones.count()
            promedio = mediciones.aggregate(avg=Avg("valor"))['avg']
            maximo = mediciones.aggregate(max=Max("valor"))['max']
            minimo = mediciones.aggregate(min=Min("valor"))['min']

            datos.append({
                "id": sensor.id,
                "nombre": sensor.nombre,
                "tipo": sensor.get_tipo_display(),
                "activo": sensor.activo,
                "valor_referencia": float(sensor.valor_referencia) if sensor.valor_referencia else None,
                "rango_minimo": float(sensor.rango_minimo) if sensor.rango_minimo else None,
                "rango_maximo": float(sensor.rango_maximo) if sensor.rango_maximo else None,
                "total_mediciones": total,
                "promedio": promedio,
                "minimo": minimo,
                "maximo": maximo,
                "estado": self.analizar_estado(sensor, promedio),
            })

        return Response({"sensores": datos})

    def analizar_estado(self, sensor, promedio):
        """
        Evalúa el estado operativo del sensor según el promedio y los rangos definidos.
        """
        if promedio is None:
            return "sin datos"

        if sensor.rango_minimo and promedio < sensor.rango_minimo:
            return "🟡 Activado (por valor bajo)"
        if sensor.rango_maximo and promedio > sensor.rango_maximo:
            return "🔴 Desactivado (por valor alto)"
        return "🟢 Estable"
