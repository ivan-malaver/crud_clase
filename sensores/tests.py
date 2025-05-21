from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Sensor, Medicion
from datetime import datetime, timedelta

User = get_user_model()

class SensorTests(APITestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Configurar cliente API autenticado
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Crear datos de prueba
        self.sensor1 = Sensor.objects.create(
            nombre="Sensor Temperatura",
            tipo="TEM",
            ubicacion="Invernadero 1",
            activo=True,
            rango_minimo=10,
            rango_maximo=30
        )
        
        self.sensor2 = Sensor.objects.create(
            nombre="Sensor Humedad",
            tipo="HUM",
            ubicacion="Invernadero 2",
            activo=False
        )
        
        # Crear mediciones de prueba
        now = datetime.now()
        self.medicion1 = Medicion.objects.create(
            sensor=self.sensor1,
            valor=25.5,
            timestamp=now - timedelta(hours=2)
        )
        self.medicion2 = Medicion.objects.create(
            sensor=self.sensor1,
            valor=15.0,
            timestamp=now - timedelta(hours=1)
        )

    def test_listar_sensores(self):
        """Test para verificar que se listan correctamente los sensores"""
        url = reverse('sensor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filtrar_sensores_por_tipo(self):
        """Test para verificar el filtrado de sensores por tipo"""
        url = reverse('sensor-list') + '?tipo=TEM'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], "Sensor Temperatura")
    
    def test_crear_sensor_valido(self):
        """Test para crear un nuevo sensor"""
        url = reverse('sensor-list')
        data = {
            'nombre': 'Nuevo Sensor',
            'tipo': 'LUZ',
            'ubicacion': 'Invernadero 3',
            'activo': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Sensor.objects.count(), 3)

    # Más pruebas como en el código original...

class SensorTemplateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = self.client
        self.sensor = Sensor.objects.create(
            nombre="Test Sensor",
            tipo="TEM",
            ubicacion="Test Location"
        )

    def test_vista_template_requiere_login(self):
        """Test que verifica que la vista template requiere autenticación"""
        url = '/sensores/'  # Ajusta según tu URL configurada
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

    def test_vista_template_con_login(self):
        """Test que verifica el acceso a la vista con login"""
        self.client.login(username='testuser', password='testpass123')
        url = '/sensores/'  # Ajusta según tu URL configurada
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sensores Registrados")
