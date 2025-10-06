"""
Tests para la API FastAPI de Shield-SMS
Metodología TDD - Fase RED
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar el directorio backend al path para importar la API
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint GET /health"""
    
    def test_health_endpoint_exists(self):
        """Verifica que el endpoint /health existe y responde"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_correct_structure(self):
        """Verifica que /health retorna la estructura correcta"""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data
    
    def test_health_endpoint_returns_correct_values(self):
        """Verifica que /health retorna los valores esperados"""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Shield-SMS API"


class TestClassifyEndpoint:
    """Tests para el endpoint POST /classify"""
    
    def test_classify_endpoint_exists(self):
        """Verifica que el endpoint /classify existe"""
        response = client.post("/classify", json={"text": "Test message"})
        assert response.status_code in [200, 422]  # 200 ok o 422 validation error
    
    def test_classify_accepts_valid_request(self):
        """Verifica que /classify acepta requests válidos"""
        response = client.post("/classify", json={"text": "Congratulations! You won a prize"})
        assert response.status_code == 200
    
    def test_classify_returns_correct_structure(self):
        """Verifica que /classify retorna la estructura correcta"""
        response = client.post("/classify", json={"text": "Hello world"})
        data = response.json()
        assert "label" in data
        assert "score" in data
        assert "text" in data
    
    def test_classify_label_is_valid(self):
        """Verifica que el label es 'smishing' o 'ham'"""
        response = client.post("/classify", json={"text": "Test message"})
        data = response.json()
        assert data["label"] in ["smishing", "ham"]
    
    def test_classify_score_is_float(self):
        """Verifica que el score es un float entre 0.0 y 1.0"""
        response = client.post("/classify", json={"text": "Test message"})
        data = response.json()
        assert isinstance(data["score"], float)
        assert 0.0 <= data["score"] <= 1.0
    
    def test_classify_returns_original_text(self):
        """Verifica que retorna el texto original"""
        test_text = "This is a test message"
        response = client.post("/classify", json={"text": test_text})
        data = response.json()
        assert data["text"] == test_text
    
    def test_classify_rejects_missing_text_field(self):
        """Verifica que rechaza requests sin campo 'text'"""
        response = client.post("/classify", json={})
        assert response.status_code == 422
    
    def test_classify_rejects_empty_text(self):
        """Verifica que rechaza requests con texto vacío"""
        response = client.post("/classify", json={"text": ""})
        assert response.status_code == 422
    
    def test_classify_rejects_whitespace_only_text(self):
        """Verifica que rechaza texto con solo espacios en blanco"""
        response = client.post("/classify", json={"text": "   "})
        assert response.status_code == 422
