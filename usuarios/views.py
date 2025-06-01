# usuarios/views.py
"""
Vistas REST alineadas con:
 ▸ Modelo Usuario (email = USERNAME_FIELD)
 ▸ Serializadores robustos (Usuario / Cliente / JWT)
 ▸ Autenticación JWT (SimpleJWT)
 ▸ Permisos por rol (admin, supervisor, cliente)
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model

from .models import Cliente
from .serializers import (
    UsuarioSerializer,
    UsuarioRegistroSerializer,
    ClienteSerializer,
    ClienteRegistroSerializer,
    EmailTokenObtainPairSerializer,
)
from .permissions import (
    IsAdminUser,
    IsSupervisorUser,
    IsClienteUser,
    IsOwnerOrAdmin,
    IsAdminOrReadOnly,
    IsOwnerClienteOnly,
)

Usuario = get_user_model()

# ────────────────────────────────────────────────────────────────
# 🔐 AUTENTICACIÓN JWT
# ────────────────────────────────────────────────────────────────
class EmailTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Autenticación con email y contraseña.
    Retorna tokens JWT (access y refresh) y el rol del usuario.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = EmailTokenObtainPairSerializer


class EmailTokenRefreshView(TokenRefreshView):
    """
    POST /api/auth/refresh/
    Refresca el token de acceso usando el token de refresh.
    """
    permission_classes = [permissions.AllowAny]


# ────────────────────────────────────────────────────────────────
# 👤 USUARIOS: Registro y gestión
# ────────────────────────────────────────────────────────────────
class UsuarioListView(generics.ListAPIView):
    """
    GET /usuarios/  → Lista todos los usuarios.
    Solo accesible por administradores o supervisores.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class UsuarioCreateView(generics.CreateAPIView):
    """
    POST /usuarios/crear/  → Registro de nuevos usuarios.
    Abierto al público.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [permissions.AllowAny]


class UsuarioDetailView(generics.RetrieveAPIView):
    """
    GET /usuarios/<pk>/  → Detalles de un usuario específico.
    Solo visible por el mismo usuario o un admin.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsOwnerOrAdmin]


class UsuarioUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /usuarios/<pk>/editar/  → Actualiza un usuario específico.
    Solo el propietario o un admin puede hacerlo.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsOwnerOrAdmin]


class UsuarioDeleteView(generics.DestroyAPIView):
    """
    DELETE /usuarios/<pk>/eliminar/  → Elimina un usuario del sistema.
    Solo permitido para administradores.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminUser]


# ────────────────────────────────────────────────────────────────
# 📦 CLIENTES: Registro y gestión
# ────────────────────────────────────────────────────────────────
class ClienteListView(generics.ListAPIView):
    """
    GET /clientes/  → Lista de clientes registrados.
    Accesible solo por admin o supervisor.
    """
    queryset = Cliente.objects.select_related("usuario")
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class ClienteCreateView(generics.CreateAPIView):
    """
    POST /clientes/crear/  → Registro de nuevo cliente (usuario + cliente).
    Abierto al público.
    """
    queryset = Cliente.objects.select_related("usuario")
    serializer_class = ClienteRegistroSerializer
    permission_classes = [permissions.AllowAny]


class ClienteDetailView(generics.RetrieveAPIView):
    """
    GET /clientes/<pk>/  → Ver detalles de un cliente.
    Solo su dueño o un admin pueden acceder.
    """
    queryset = Cliente.objects.select_related("usuario")
    serializer_class = ClienteSerializer
    permission_classes = [IsOwnerClienteOnly | IsAdminUser]


class ClienteUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /clientes/<pk>/editar/  → Actualiza datos del cliente.
    Protege el campo usuario y valida por dueño o admin.
    """
    queryset = Cliente.objects.select_related("usuario")
    serializer_class = ClienteSerializer
    permission_classes = [IsOwnerClienteOnly | IsAdminUser]

    def update(self, request, *args, **kwargs):
        partial = request.method == "PATCH"
        instance = self.get_object()
        payload = {k: v for k, v in request.data.items() if k != "usuario"}
        serializer = self.get_serializer(instance, data=payload, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClienteDeleteView(generics.DestroyAPIView):
    """
    DELETE /clientes/<pk>/eliminar/  → Elimina un cliente del sistema.
    Solo permitido para administradores.
    """
    queryset = Cliente.objects.select_related("usuario")
    serializer_class = ClienteSerializer
    permission_classes = [IsAdminUser]


class ClienteDetailByUserView(generics.RetrieveAPIView):
    """
    GET /clientes/user/<user_id>/  → Acceso por ID de usuario.
    Útil para vincular interfaces personales de cliente.
    """
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerClienteOnly | IsAdminUser]

    def get_object(self):
        user_id = self.kwargs["user_id"]
        return get_object_or_404(Cliente.objects.select_related("usuario"), usuario__id=user_id)