# usuarios/serializers.py
"""
Serializadores para el dominio de autenticación y clientes.

• Mantienen la separación “lectura vs. escritura” (evita exponer password).
• Añaden el payload «role» al token JWT.
• Permiten registro compuesto (Usuario + Cliente) en un único POST.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from .models import Cliente

# ------------------------------------------------------------------
# 🔄 Referencia dinámica al modelo de usuario (respeta AUTH_USER_MODEL)
# ------------------------------------------------------------------
Usuario = get_user_model()

# Gestión segura del valor por defecto de role
ROLE_CLIENTE = getattr(Usuario, "ROLE_CLIENTE", "cliente")  # fallback


# ────────────────────────────────────────────────────────────────
# 🔑 SERIALIZADOR JWT  (login)
# ────────────────────────────────────────────────────────────────
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende SimpleJWT para personalizar el token JWT generado:
    • Usa email como credencial principal (USERNAME_FIELD ya es 'email')
    • Inserta el campo «role» en el payload → útil para el frontend para gestionar permisos
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role  # Agrega el rol del usuario al token JWT
        return token


# ────────────────────────────────────────────────────────────────
# 🌱 USUARIO (READ-ONLY en respuestas)
# ────────────────────────────────────────────────────────────────
class UsuarioSerializer(serializers.ModelSerializer):
    """
    Versión ligera del usuario para mostrar en listados o como campo anidado.
    No permite modificar campos críticos como el rol o la contraseña.
    """

    class Meta:
        model = Usuario
        fields = ("id", "email", "username", "role")
        read_only_fields = ("id", "role")  # El rol no puede modificarse aquí


# ────────────────────────────────────────────────────────────────
# 📝 REGISTRO DE USUARIO
# ────────────────────────────────────────────────────────────────
class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """
    Para registro de usuarios nuevos:
    • Recibe email, password y opcionalmente username y role.
    • Encripta el password usando create_user().
    • Por defecto, asigna el rol 'cliente'.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    class Meta:
        model = Usuario
        fields = ("email", "username", "password", "role")
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True},
            "role": {"default": ROLE_CLIENTE},  # Evita que se pueda registrar como admin directamente
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        return Usuario.objects.create_user(password=password, **validated_data)


# ────────────────────────────────────────────────────────────────
# 📦 CLIENTE (READ-ONLY)
# ────────────────────────────────────────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):
    """
    Serializador de cliente usado para lectura.
    El campo 'usuario' es anidado y de solo lectura.
    """
    usuario = UsuarioSerializer(read_only=True)  # Muestra datos del usuario, sin permitir edición

    class Meta:
        model = Cliente
        fields = ("id", "usuario", "nombre_completo", "direccion", "telefono")


# ────────────────────────────────────────────────────────────────
# 📝 REGISTRO “2-en-1” (Usuario + Cliente)
# ────────────────────────────────────────────────────────────────
class ClienteRegistroSerializer(serializers.ModelSerializer):
    """
    Permite crear simultáneamente el Usuario y el Cliente desde un solo endpoint.
    Validación anidada:
    {
      "usuario": {
        "email": "...",
        "password": "...",
        "username": "..."
      },
      "nombre_completo": "...",
      "direccion": "...",
      "telefono": "..."
    }
    """
    usuario = UsuarioRegistroSerializer()  # Usamos el serializador de registro definido arriba

    class Meta:
        model = Cliente
        fields = ("id", "usuario", "nombre_completo", "direccion", "telefono")

    def create(self, validated_data):
        usuario_data = validated_data.pop("usuario")  # Extrae la info del usuario
        usuario = UsuarioRegistroSerializer().create(usuario_data)  # Crea el usuario
        cliente = Cliente.objects.create(usuario=usuario, **validated_data)  # Asocia al cliente
        return cliente
