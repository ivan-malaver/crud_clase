"""
Rutas RESTful para el módulo de Control de Calidad 🧪

Incluye:
- Endpoints funcionales para CRUD de lotes procesados
- Ruta para enviar informe PDF por correo electrónico
- Compatible con Django 4+ y DRF
"""

from django.urls import path
from .views import (
    listar_lotes,
    registrar_lote,
    detalle_lote,
    actualizar_lote,
    eliminar_lote,
    enviar_informe_pdf,
)

# ──────────────────────────────────────────────
# RUTAS REST FUNCIONALES
# ──────────────────────────────────────────────
urlpatterns = [

    # 📋 Listado y creación
    path("lotes/", listar_lotes, name="lote-list"),
    path("lotes/registrar/", registrar_lote, name="lote-create"),

    # 🔍 Operaciones por ID
    path("lotes/<int:pk>/", detalle_lote, name="lote-detail"),
    path("lotes/<int:pk>/editar/", actualizar_lote, name="lote-update"),
    path("lotes/<int:pk>/eliminar/", eliminar_lote, name="lote-delete"),

    # 📤 Envío del informe en PDF por correo
    path("lotes/<int:pk>/enviar-informe/", enviar_informe_pdf, name="lote-send-informe"),
]
