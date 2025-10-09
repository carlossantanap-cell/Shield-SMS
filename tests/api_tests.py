"""
Tests para la API FastAPI de Shield-SMS
Metodología TDD - Fase REFACTOR con casos edge
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar el directorio backend al path para importar la API
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.main import app


@pytest.fixture
def client():
    """Fixture para crear el cliente de pruebas"""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint GET /health"""
    
    def test_health_endpoint_exists(self, client):
        """Verifica que el endpoint /health existe y responde"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_correct_structure(self, client):
        """Verifica que /health retorna la estructura correcta"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"
        assert "service" in data
    
    def test_health_endpoint_returns_json(self, client):
        """Verifica que /health retorna JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"


class TestClassifyEndpoint:
    """Tests para el endpoint POST /classify"""
    
    def test_classify_endpoint_exists(self, client):
        """Verifica que el endpoint /classify existe"""
        response = client.post("/classify", json={"text": "Hola"})
        assert response.status_code == 200
    
    def test_classify_requires_text_field(self, client):
        """Verifica que /classify requiere el campo 'text'"""
        response = client.post("/classify", json={})
        assert response.status_code == 422
    
    def test_classify_returns_correct_structure(self, client):
        """Verifica que /classify retorna la estructura correcta"""
        response = client.post("/classify", json={"text": "Hola mundo"})
        assert response.status_code == 200
        data = response.json()
        assert "label" in data
        assert "score" in data
        assert "text" in data
    
    def test_classify_smishing_message(self, client):
        """Verifica clasificación de mensaje smishing obvio"""
        mensaje = "URGENTE: Tu cuenta ha sido bloqueada. Haz clic aquí: http://bit.ly/fake123"
        response = client.post("/classify", json={"text": mensaje})
        assert response.status_code == 200
        data = response.json()
        assert data["label"] in ["smishing", "spam"]
    
    def test_classify_ham_message(self, client):
        """Verifica clasificación de mensaje legítimo"""
        mensaje = "Hola mamá, llegaré tarde a casa hoy. Te quiero."
        response = client.post("/classify", json={"text": mensaje})
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "ham"
    
    def test_classify_empty_text(self, client):
        """Verifica manejo de texto vacío"""
        response = client.post("/classify", json={"text": ""})
        assert response.status_code == 422
    
    def test_classify_very_long_text(self, client):
        """Verifica manejo de texto muy largo"""
        texto_largo = "A" * 10000
        response = client.post("/classify", json={"text": texto_largo})
        assert response.status_code == 422
    
    def test_classify_special_characters(self, client):
        """Verifica manejo de caracteres especiales"""
        texto = "¡Hola! ¿Cómo estás? 😊 #Python @user"
        response = client.post("/classify", json={"text": texto})
        assert response.status_code == 200
    
    def test_classify_with_urls(self, client):
        """Verifica detección de URLs en mensajes"""
        texto = "Visita https://example.com para más info"
        response = client.post("/classify", json={"text": texto})
        assert response.status_code == 200
    
    def test_classify_with_phone_numbers(self, client):
        """Verifica detección de números telefónicos"""
        texto = "Llama al 999-888-777 para confirmar"
        response = client.post("/classify", json={"text": texto})
        assert response.status_code == 200
    
    def test_classify_with_money_amounts(self, client):
        """Verifica detección de montos de dinero"""
        texto = "Has ganado $1000 dólares. Reclama ahora."
        response = client.post("/classify", json={"text": texto})
        assert response.status_code == 200


class TestAPIPerformance:
    """Tests de rendimiento de la API"""
    
    def test_response_time_under_threshold(self, client):
        """Verifica que el tiempo de respuesta es aceptable"""
        import time
        start = time.time()
        response = client.post("/classify", json={"text": "Mensaje de prueba"})
        elapsed = time.time() - start
        assert elapsed < 1.0  # Menos de 1 segundo
        assert response.status_code == 200
    
    def test_multiple_requests(self, client):
        """Verifica que la API maneja múltiples requests"""
        for i in range(10):
            response = client.post("/classify", json={"text": f"Mensaje {i}"})
            assert response.status_code == 200


class TestAPIEdgeCases:
    """Tests de casos edge de la API"""
    
    def test_classify_only_emojis(self, client):
        """Verifica manejo de solo emojis"""
        response = client.post("/classify", json={"text": "😊😂🎉"})
        assert response.status_code == 200
    
    def test_classify_only_numbers(self, client):
        """Verifica manejo de solo números"""
        response = client.post("/classify", json={"text": "123456789"})
        assert response.status_code == 200
    
    def test_classify_mixed_languages(self, client):
        """Verifica manejo de múltiples idiomas"""
        response = client.post("/classify", json={"text": "Hello mundo 你好"})
        assert response.status_code == 200
    
    def test_classify_multiline_text(self, client):
        """Verifica manejo de texto multilínea"""
        texto = "Línea 1\nLínea 2\nLínea 3"
        response = client.post("/classify", json={"text": texto})
        assert response.status_code == 200
