"""
Archivo principal de enrutamiento del proyecto Django AgroSENA.
Organiza:
- Login/logout/registro
- Vistas base (inicio, dashboard)
- Rutas modulares: sensores, clima, plagas, cosechas, control de calidad
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    # 🔐 LOGIN
    path('login/', LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True
    ), name='login'),

    # 🔐 LOGOUT
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # 🏠 INICIO
    path('', TemplateView.as_view(template_name='index.html'), name='home'),

    # 🆕 REGISTRO
    path('registro/', TemplateView.as_view(template_name='registro.html'), name='registro'),

    # 🧭 DASHBOARD PRINCIPAL
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    
     # 🧭 DASHBOARD PRINCIPAL
    path('sensor_list/', TemplateView.as_view(template_name='sensor_list.html'), name='sensor_list'),


    # ⚙️ ADMIN DE DJANGO
    path('admin/', admin.site.urls),

    # 📁 API DE USUARIOS
    path('api1/', include('usuarios.urls')),

    # 🌡️ API DE SENSORES
    path('api2/', include('sensores.urls')),

    # ☁️ API DE CLIMA
    path('api3/', include('clima.urls')),

    # 🐛 API DE PLAGAS
    path('api4/', include('plagas.urls')),

    # 🌾 API DE COSECHAS
    path('cosecha/', include('cosechas.urls')),

    # 📦 API DE CONTROL DE CALIDAD
    path('api6/', include('control_calidad.urls')),
]
