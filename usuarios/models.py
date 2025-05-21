# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Usuario corporativo:
    ▸ El **e-mail** sustituye al username como credencial primaria.
    ▸ Se añade el campo «role» para segmentar permisos / UI.
    ▸ Este campo servirá para manejar los permisos avanzados.
    """

    # ─────────────────────────────────────────────────────────────
    # 1️⃣ Credencial principal
    # ─────────────────────────────────────────────────────────────
    email = models.EmailField(
        unique=True,                         # evita duplicados de correo
        error_messages={
            "unique": "Ya existe un usuario con este e-mail.",
        },
    )

    # ─────────────────────────────────────────────────────────────
    # 2️⃣ Rol de negocio (permite controlar accesos a recursos)
    # ─────────────────────────────────────────────────────────────
    ROLE_CLIENTE = "cliente"
    ROLE_ADMIN   = "admin"
    ROLE_SUPERVISOR = "supervisor"  # Nuevo rol agregado para mayor granularidad

    ROLE_CHOICES = [
        (ROLE_CLIENTE, "Cliente"),
        (ROLE_ADMIN,   "Administrador"),
        (ROLE_SUPERVISOR, "Supervisor"),  # Puede ver sensores y usuarios, pero no modificarlos
    ]

    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENTE,              # Por defecto, los nuevos usuarios serán clientes
        help_text="Define el nivel de acceso del usuario (cliente, admin o supervisor)."
    )

    # ─────────────────────────────────────────────────────────────
    # 3️⃣ Ajustes de autenticación
    # ─────────────────────────────────────────────────────────────
    USERNAME_FIELD  = "email"   # ← login por e-mail
    REQUIRED_FIELDS = ["username"]  # sigue pidiendo username en createsuperuser

    # TIP: si NO quieres usar «username» nunca, deja el campo pero opcional:
    # username: models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.email} ({self.role})"


class Cliente(models.Model):
    """
    Datos extra para usuarios con rol «cliente».
    Se borra en cascada si el Usuario desaparece.
    """

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="cliente",  # Permite acceder al cliente desde el usuario: user.cliente
    )

    nombre_completo = models.CharField(max_length=100)
    direccion       = models.CharField(max_length=255, blank=True)
    telefono        = models.CharField(max_length=15,  blank=True)

    def __str__(self):
        return f"Cliente: {self.nombre_completo}"
