# usuarios/stats.py
"""
Vista de estadísticas para usuarios del sistema.
Incluye:
- Conteo total de usuarios
- Conteo por rol (admin, supervisor, cliente)
- Conteo por permisos personalizados (según el modelo Usuario)
- Último ingreso (last_login)
- Fecha de creación

Requiere autenticación y rol de administrador.
"""

from django.utils.timezone import now
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUser
from collections import Counter

Usuario = get_user_model()

class UsuarioStatsView(APIView):
    """
    GET /api/usuarios/stats/  → Devuelve estadísticas generales del sistema de usuarios.
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        usuarios = Usuario.objects.all()
        total = usuarios.count()

        # Conteo por rol
        roles = usuarios.values_list("role", flat=True)
        conteo_roles = Counter(roles)

        # Últimos accesos
        ultimos_login = usuarios.exclude(last_login__isnull=True).order_by('-last_login')[:5]
        recientes = [
            {
                "email": u.email,
                "role": u.role,
                "last_login": u.last_login,
            }
            for u in ultimos_login
        ]

        # Usuarios más antiguos
        creados_primero = usuarios.order_by('date_joined')[:5]
        veteranos = [
            {
                "email": u.email,
                "role": u.role,
                "date_joined": u.date_joined,
            }
            for u in creados_primero
        ]

        return Response({
            "total_usuarios": total,
            "por_rol": conteo_roles,
            "ultimos_login": recientes,
            "usuarios_mas_antiguos": veteranos,
        })
