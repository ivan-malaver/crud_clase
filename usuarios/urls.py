# usuarios/urls.py
"""
Rutas para el módulo de autenticación y gestión de usuarios/clientes.

Organización RESTful:
- Autenticación JWT (login y refresh)
- CRUD de usuarios (con separación por método)
- CRUD de clientes (con separación por método)
- Estadísticas del sistema

Se utiliza namespace 'usuarios' para evitar colisiones si se incluye en el proyecto principal.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    EmailTokenObtainPairView,
    EmailTokenRefreshView,
    # Usuarios
    UsuarioListView,
    UsuarioCreateView,
    UsuarioDetailView,
    UsuarioUpdateView,
    UsuarioDeleteView,
    # Clientes
    ClienteListView,
    ClienteCreateView,
    ClienteDetailView,
    ClienteUpdateView,
    ClienteDeleteView,
    ClienteDetailByUserView,
)
from .stats import UsuarioStatsView  # 📊 Nueva vista de estadísticas

app_name = "usuarios"  # Permite usar reverse('usuarios:nombre')

urlpatterns = [
    # ─────────────────────────────────────────────────────────────
    # 🔐 AUTENTICACIÓN JWT
    # ─────────────────────────────────────────────────────────────
    path("auth/login/", EmailTokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", EmailTokenRefreshView.as_view(), name="token-refresh"),

    # ─────────────────────────────────────────────────────────────
    # 👤 USUARIOS
    # ─────────────────────────────────────────────────────────────
    path("usuarios/", UsuarioListView.as_view(), name="usuario-list"),      # GET
    path("usuarios/crear/", UsuarioCreateView.as_view(), name="usuario-create"),  # POST
    path("usuarios/<int:pk>/", UsuarioDetailView.as_view(), name="usuario-detail"),  # GET
    path("usuarios/<int:pk>/editar/", UsuarioUpdateView.as_view(), name="usuario-update"),  # PUT/PATCH
    path("usuarios/<int:pk>/eliminar/", UsuarioDeleteView.as_view(), name="usuario-delete"),  # DELETE

    # Ruta adicional para estadísticas de usuarios
    path("usuarios/stats/", UsuarioStatsView.as_view(), name="usuario-stats"),  # 📊 GET

    # ─────────────────────────────────────────────────────────────
    # 📦 CLIENTES
    # ─────────────────────────────────────────────────────────────
    path("clientes/", ClienteListView.as_view(), name="cliente-list"),  # GET
    path("clientes/crear/", ClienteCreateView.as_view(), name="cliente-create"),  # POST
    path("clientes/<int:pk>/", ClienteDetailView.as_view(), name="cliente-detail"),  # GET
    path("clientes/<int:pk>/editar/", ClienteUpdateView.as_view(), name="cliente-update"),  # PUT/PATCH
    path("clientes/<int:pk>/eliminar/", ClienteDeleteView.as_view(), name="cliente-delete"),  # DELETE

    # Ruta especial para obtener cliente por ID de usuario
    path("clientes/user/<int:user_id>/", ClienteDetailByUserView.as_view(), name="cliente-by-user"),
]