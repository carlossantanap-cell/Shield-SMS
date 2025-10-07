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


class TestClassifyEdgeCases:
    """Tests para casos edge del endpoint /classify"""
    
    def test_classify_rejects_very_long_text(self):
        """Verifica que rechaza texto muy largo (>1000 caracteres)"""
        long_text = "A" * 1001
        response = client.post("/classify", json={"text": long_text})
        assert response.status_code == 422
    
    def test_classify_accepts_max_length_text(self):
        """Verifica que acepta texto de exactamente 1000 caracteres"""
        max_text = "A" * 1000
        response = client.post("/classify", json={"text": max_text})
        assert response.status_code == 200
    
    def test_classify_accepts_single_character(self):
        """Verifica que acepta texto de un solo carácter"""
        response = client.post("/classify", json={"text": "A"})
        assert response.status_code == 200
    
    def test_classify_handles_special_characters(self):
        """Verifica que maneja correctamente caracteres especiales"""
        special_text = "Hello! @#$%^&*() <> {} [] | \\ / ? ~ `"
        response = client.post("/classify", json={"text": special_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == special_text
    
    def test_classify_handles_emojis(self):
        """Verifica que maneja correctamente emojis"""
        emoji_text = "Hello 👋 World 🌍 Test 🎉"
        response = client.post("/classify", json={"text": emoji_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == emoji_text
    
    def test_classify_handles_unicode_characters(self):
        """Verifica que maneja correctamente caracteres Unicode"""
        unicode_text = "Hola ñ á é í ó ú ü 你好 مرحبا"
        response = client.post("/classify", json={"text": unicode_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == unicode_text
    
    def test_classify_handles_newlines_and_tabs(self):
        """Verifica que maneja correctamente saltos de línea y tabulaciones"""
        multiline_text = "Line 1\nLine 2\tTabbed\rCarriage return"
        response = client.post("/classify", json={"text": multiline_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == multiline_text
    
    def test_classify_handles_mixed_languages(self):
        """Verifica que maneja correctamente texto en diferentes idiomas"""
        mixed_text = "English, Español, Français, Deutsch, 日本語, 中文"
        response = client.post("/classify", json={"text": mixed_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == mixed_text
    
    def test_classify_handles_numbers_only(self):
        """Verifica que maneja correctamente texto con solo números"""
        numbers_text = "1234567890"
        response = client.post("/classify", json={"text": numbers_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == numbers_text
    
    def test_classify_handles_urls(self):
        """Verifica que maneja correctamente URLs en el texto"""
        url_text = "Visit https://example.com or http://test.org for more info"
        response = client.post("/classify", json={"text": url_text})
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == url_text
    
    def test_classify_response_schema_validation(self):
        """Verifica que la respuesta cumple con el schema completo"""
        response = client.post("/classify", json={"text": "Test message"})
        assert response.status_code == 200
        data = response.json()
        
        # Verificar tipos de datos
        assert isinstance(data["label"], str)
        assert isinstance(data["score"], float)
        assert isinstance(data["text"], str)
        
        # Verificar valores válidos
        assert data["label"] in ["smishing", "ham"]
        assert 0.0 <= data["score"] <= 1.0
        assert len(data["text"]) > 0
