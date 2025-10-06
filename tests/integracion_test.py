
"""
Tests de Integración Completa - Shield-SMS
Autor: Alexandro Achalma (alexandro.achalma.g@uni.pe)
Metodología: TDD (Test-Driven Development)

Tests que verifican la integración completa del sistema:
- Flujo completo: texto → PLN → Modelo → clasificación
- Integración API + PLN + Modelo
- Validación de URLs y utilidades
- Rendimiento y casos edge
"""

import pytest
import json
import time
import sys
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Agregar el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Importar módulos del sistema
from PLN.preprocessing import preprocesar_completo
from ModeloML.rules_model import classify
from utils.url_check import (
    es_url_sospechosa,
    es_url_acortada,
    extraer_dominio,
    validar_url,
    analizar_url_completo
)


# Fixture para cargar datos mock
@pytest.fixture
def mock_sms_data() -> List[Dict[str, str]]:
    """
    Carga los mensajes SMS de prueba desde mock_sms.json.
    
    Returns:
        Lista de diccionarios con 'text' y 'expected_label'
    """
    mock_file = Path(__file__).parent / "mock_sms.json"
    with open(mock_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def smishing_messages(mock_sms_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filtra solo mensajes de smishing."""
    return [msg for msg in mock_sms_data if msg["expected_label"] == "smishing"]


@pytest.fixture
def ham_messages(mock_sms_data: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Filtra solo mensajes legítimos (ham)."""
    return [msg for msg in mock_sms_data if msg["expected_label"] == "ham"]


# ============================================================================
# TESTS DE FLUJO COMPLETO
# ============================================================================

def test_flujo_completo_smishing(smishing_messages: List[Dict[str, str]]):
    """
    Test RED: Verifica el flujo completo para mensajes de smishing.
    
    Flujo: texto → PLN.preprocesar_completo() → Modelo.classify() → verificar label="smishing"
    
    Este test DEBE FALLAR inicialmente porque:
    - backend/utils/url_check.py no existe
    - La integración completa no está implementada
    """
    errores = []
    
    for i, mensaje in enumerate(smishing_messages):
        texto = mensaje["text"]
        expected = mensaje["expected_label"]
        
        # Flujo completo: PLN → Modelo
        texto_procesado = preprocesar_completo(texto)
        resultado = classify(texto)
        
        # Verificar que se clasificó como smishing
        if resultado["label"] != expected:
            errores.append(
                f"Mensaje {i+1}: Esperado '{expected}', obtenido '{resultado['label']}'\n"
                f"  Texto: {texto[:80]}...\n"
                f"  Score: {resultado['score']}"
            )
    
    # Reportar todos los errores
    if errores:
        pytest.fail(
            f"\n{len(errores)} de {len(smishing_messages)} mensajes smishing mal clasificados:\n" +
            "\n".join(errores)
        )


def test_flujo_completo_ham(ham_messages: List[Dict[str, str]]):
    """
    Test RED: Verifica el flujo completo para mensajes legítimos (ham).
    
    Flujo: texto → PLN.preprocesar_completo() → Modelo.classify() → verificar label="ham"
    """
    errores = []
    
    for i, mensaje in enumerate(ham_messages):
        texto = mensaje["text"]
        expected = mensaje["expected_label"]
        
        # Flujo completo: PLN → Modelo
        texto_procesado = preprocesar_completo(texto)
        resultado = classify(texto)
        
        # Verificar que se clasificó como ham
        if resultado["label"] != expected:
            errores.append(
                f"Mensaje {i+1}: Esperado '{expected}', obtenido '{resultado['label']}'\n"
                f"  Texto: {texto[:80]}...\n"
                f"  Score: {resultado['score']}"
            )
    
    # Reportar todos los errores
    if errores:
        pytest.fail(
            f"\n{len(errores)} de {len(ham_messages)} mensajes ham mal clasificados:\n" +
            "\n".join(errores)
        )


def test_integracion_api_pln_modelo():
    """
    Test RED: Verifica la integración entre API, PLN y Modelo.
    
    Simula un request a la API y verifica que integra correctamente
    PLN y Modelo para producir una respuesta válida.
    """
    # Mensaje de prueba
    texto_prueba = "URGENT! Click here to claim your $1000 prize: http://bit.ly/prize123"
    
    # Simular el flujo de la API
    # 1. Validar entrada (ya lo hace Pydantic en la API)
    assert len(texto_prueba) > 0
    assert len(texto_prueba) <= 1000
    
    # 2. Procesar con PLN
    texto_procesado = preprocesar_completo(texto_prueba)
    assert texto_procesado is not None
    assert isinstance(texto_procesado, str)
    
    # 3. Clasificar con Modelo
    resultado = classify(texto_prueba)
    
    # 4. Verificar estructura de respuesta
    assert "label" in resultado
    assert "score" in resultado
    assert resultado["label"] in ["smishing", "ham"]
    assert 0.0 <= resultado["score"] <= 1.0
    
    # 5. Verificar que detecta smishing
    assert resultado["label"] == "smishing", \
        f"Debería detectar smishing, obtuvo: {resultado['label']} (score: {resultado['score']})"


def test_accuracy_mock_data(mock_sms_data: List[Dict[str, str]]):
    """
    Test RED: Verifica que el sistema tiene al menos 90% de accuracy en datos mock.
    
    Este test mide la precisión general del sistema completo.
    """
    correctos = 0
    total = len(mock_sms_data)
    errores_detallados = []
    
    for mensaje in mock_sms_data:
        texto = mensaje["text"]
        expected = mensaje["expected_label"]
        
        resultado = classify(texto)
        
        if resultado["label"] == expected:
            correctos += 1
        else:
            errores_detallados.append({
                "texto": texto[:80],
                "esperado": expected,
                "obtenido": resultado["label"],
                "score": resultado["score"]
            })
    
    accuracy = (correctos / total) * 100
    
    # Verificar accuracy mínimo del 90%
    assert accuracy >= 90.0, \
        f"Accuracy: {accuracy:.2f}% (esperado >= 90%)\n" \
        f"Correctos: {correctos}/{total}\n" \
        f"Primeros errores: {errores_detallados[:5]}"


# ============================================================================
# TESTS DE RENDIMIENTO
# ============================================================================

def test_tiempo_respuesta():
    """
    Test RED: Verifica que clasificar un mensaje toma menos de 100ms.
    
    El sistema debe ser rápido para uso en producción.
    """
    texto_prueba = "Click here to win $1000! http://bit.ly/win"
    
    # Medir tiempo de clasificación
    inicio = time.time()
    resultado = classify(texto_prueba)
    tiempo_transcurrido = (time.time() - inicio) * 1000  # en milisegundos
    
    assert tiempo_transcurrido < 100, \
        f"Clasificación tomó {tiempo_transcurrido:.2f}ms (esperado < 100ms)"
    
    # Verificar que el resultado es válido
    assert resultado["label"] in ["smishing", "ham"]


def test_rendimiento_batch(mock_sms_data: List[Dict[str, str]]):
    """
    Test RED: Verifica que clasificar 100 mensajes toma menos de 5 segundos.
    """
    # Tomar los primeros 30 mensajes y repetirlos para llegar a ~100
    mensajes = (mock_sms_data * 4)[:100]
    
    inicio = time.time()
    for mensaje in mensajes:
        classify(mensaje["text"])
    tiempo_total = time.time() - inicio
    
    assert tiempo_total < 5.0, \
        f"Clasificar 100 mensajes tomó {tiempo_total:.2f}s (esperado < 5s)"


def test_concurrencia_api():
    """
    Test RED: Verifica que el sistema maneja múltiples requests simultáneos.
    
    Simula 10 requests concurrentes a la API.
    """
    mensajes_prueba = [
        "Click here to win!",
        "Hello, how are you?",
        "URGENT: Verify your account",
        "See you tomorrow",
        "Free prize! Call now!"
    ] * 2  # 10 mensajes
    
    resultados = []
    errores = []
    
    def clasificar_mensaje(texto: str) -> Dict[str, Any]:
        try:
            return classify(texto)
        except Exception as e:
            return {"error": str(e)}
    
    # Ejecutar clasificaciones en paralelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(clasificar_mensaje, msg) for msg in mensajes_prueba]
        
        for future in as_completed(futures):
            resultado = future.result()
            if "error" in resultado:
                errores.append(resultado["error"])
            else:
                resultados.append(resultado)
    
    # Verificar que no hubo errores
    assert len(errores) == 0, f"Errores en concurrencia: {errores}"
    
    # Verificar que todos los resultados son válidos
    assert len(resultados) == len(mensajes_prueba)
    for resultado in resultados:
        assert "label" in resultado
        assert resultado["label"] in ["smishing", "ham"]


# ============================================================================
# TESTS DE VALIDACIÓN DE URLs
# ============================================================================

def test_validacion_url_sospechosa():
    """
    Test RED: Verifica que es_url_sospechosa() detecta URLs maliciosas.
    
    Este test DEBE FALLAR porque backend/utils/url_check.py no existe.
    """
    # URLs sospechosas
    assert es_url_sospechosa("http://bit.ly/malware123") == True
    assert es_url_sospechosa("http://192.168.1.1/phishing") == True
    assert es_url_sospechosa("http://fake-bank-secure.com") == True
    assert es_url_sospechosa("http://goo.gl/xyz") == True
    
    # URLs confiables
    assert es_url_sospechosa("https://www.google.com") == False
    assert es_url_sospechosa("https://www.facebook.com") == False
    assert es_url_sospechosa("https://www.amazon.com") == False


def test_validacion_url_acortada():
    """
    Test RED: Verifica que es_url_acortada() detecta URLs acortadas.
    """
    # URLs acortadas
    assert es_url_acortada("http://bit.ly/abc123") == True
    assert es_url_acortada("http://tinyurl.com/xyz") == True
    assert es_url_acortada("http://goo.gl/test") == True
    assert es_url_acortada("https://t.co/abcd") == True
    
    # URLs normales
    assert es_url_acortada("https://www.google.com/search") == False
    assert es_url_acortada("https://github.com/user/repo") == False


def test_extraer_dominio():
    """
    Test RED: Verifica que extraer_dominio() extrae correctamente el dominio.
    """
    assert extraer_dominio("https://www.google.com/search") == "google.com"
    assert extraer_dominio("http://bit.ly/abc") == "bit.ly"
    assert extraer_dominio("https://subdomain.example.com/path") == "example.com"
    assert extraer_dominio("www.facebook.com") == "facebook.com"


def test_validar_url():
    """
    Test RED: Verifica que validar_url() valida el formato de URLs.
    """
    # URLs válidas
    assert validar_url("https://www.google.com") == True
    assert validar_url("http://example.com") == True
    assert validar_url("www.facebook.com") == True
    
    # URLs inválidas
    assert validar_url("not a url") == False
    assert validar_url("htp://invalid") == False
    assert validar_url("") == False


def test_analizar_url_completo():
    """
    Test RED: Verifica que analizar_url_completo() retorna análisis completo.
    """
    # URL sospechosa acortada
    resultado = analizar_url_completo("http://bit.ly/malware")
    assert resultado["es_sospechosa"] == True
    assert resultado["es_acortada"] == True
    assert resultado["dominio"] == "bit.ly"
    assert resultado["score_riesgo"] > 0.5
    
    # URL confiable
    resultado = analizar_url_completo("https://www.google.com")
    assert resultado["es_sospechosa"] == False
    assert resultado["es_acortada"] == False
    assert resultado["dominio"] == "google.com"
    assert resultado["score_riesgo"] < 0.3


# ============================================================================
# TESTS DE CASOS EDGE
# ============================================================================

def test_texto_vacio():
    """
    Test RED: Verifica manejo de texto vacío.
    """
    resultado = classify("")
    assert resultado["label"] in ["smishing", "ham"]
    assert resultado["score"] >= 0.0


def test_texto_muy_largo():
    """
    Test RED: Verifica manejo de texto muy largo (>1000 caracteres).
    """
    texto_largo = "A" * 1500
    resultado = classify(texto_largo)
    assert resultado["label"] in ["smishing", "ham"]


def test_solo_emojis():
    """
    Test RED: Verifica manejo de texto con solo emojis.
    """
    texto_emojis = "😀😃😄😁🎉🎊"
    resultado = classify(texto_emojis)
    assert resultado["label"] in ["smishing", "ham"]


def test_caracteres_especiales():
    """
    Test RED: Verifica manejo de caracteres especiales.
    """
    texto_especial = "¡¿@#$%^&*()_+-=[]{}|;:',.<>?/~`"
    resultado = classify(texto_especial)
    assert resultado["label"] in ["smishing", "ham"]


def test_texto_multilinea():
    """
    Test RED: Verifica manejo de texto con múltiples líneas.
    """
    texto_multilinea = """URGENT!
    Click here to win $1000
    http://bit.ly/prize
    Reply NOW!"""
    resultado = classify(texto_multilinea)
    assert resultado["label"] == "smishing"


def test_mezcla_idiomas():
    """
    Test RED: Verifica manejo de texto con mezcla de idiomas.
    """
    texto_mixto = "Hello! Ganaste un premio. Click here: http://bit.ly/win"
    resultado = classify(texto_mixto)
    assert resultado["label"] == "smishing"
