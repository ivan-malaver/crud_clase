# usuarios/permissions.py
"""
Este archivo define permisos personalizados para controlar el acceso a las vistas
del sistema según el rol del usuario: admin, cliente o supervisor.

Cada clase hereda de BasePermission de DRF y evalúa si el usuario tiene
los privilegios suficientes para ejecutar la operación.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'admin'.
    Equivalente a superusuarios o personal administrativo.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsSupervisorUser(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'supervisor'.
    Este rol puede ser usado para monitoreo o acceso de solo lectura.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'supervisor'


class IsClienteUser(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'cliente'.
    Por ejemplo, en vistas de perfil o datos personales.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'cliente'


class IsAdminOrReadOnly(BasePermission):
    """
    Permite acceso total si es admin, o solo lectura (GET, HEAD, OPTIONS) para otros.
    Muy útil para vistas públicas con edición restringida.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  # Permitir lectura a cualquiera autenticado
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(BasePermission):
    """
    Permite que un usuario vea/edite su propio recurso (por ejemplo, perfil),
    o que un admin pueda verlo/editarlo todo.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            obj.usuario == request.user or request.user.role == 'admin'
        )


class IsOwnerClienteOnly(BasePermission):
    """
    Permite que un cliente acceda solo a su propio objeto Cliente.
    Bloquea el acceso cruzado entre clientes.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.usuario == request.user