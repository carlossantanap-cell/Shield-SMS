"""
Tests para el Modelo ML basado en Reglas - Detección de Smishing
Metodología TDD - Fase RED
Colaborador: Juan Gonzales (j.gonzales.avendano@uni.pe)
"""

import pytest
from typing import Dict, List, Any
import os
import sys

# Agregar el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ModeloML.rules_model import classify, analizar_dataset, get_model_info, evaluar_modelo


class TestClassifyBasic:
    """Tests básicos de la función classify"""
    
    def test_classify_retorna_dict(self):
        """Verificar que classify retorna un diccionario"""
        result = classify("Hola, ¿cómo estás?")
        assert isinstance(result, dict)
    
    def test_classify_tiene_campos_requeridos(self):
        """Verificar que el resultado tiene los campos label, score y reasons"""
        result = classify("Mensaje de prueba")
        assert "label" in result
        assert "score" in result
        assert "reasons" in result
    
    def test_classify_label_valido(self):
        """Verificar que label es 'smishing' o 'ham'"""
        result = classify("Mensaje de prueba")
        assert result["label"] in ["smishing", "ham"]
    
    def test_classify_score_en_rango(self):
        """Verificar que score está entre 0.0 y 1.0"""
        result = classify("Mensaje de prueba")
        assert 0.0 <= result["score"] <= 1.0
    
    def test_classify_reasons_es_lista(self):
        """Verificar que reasons es una lista"""
        result = classify("Mensaje de prueba")
        assert isinstance(result["reasons"], list)


class TestClassifySpamMessages:
    """Tests con mensajes claramente spam del dataset"""
    
    def test_mensaje_con_url_sospechosa(self):
        """Mensaje con URL debe ser clasificado como smishing"""
        mensaje = "URGENT! You have won $5000. Click here: http://bit.ly/claim-prize"
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5
        assert "url_detectada" in result["reasons"]
    
    def test_mensaje_con_palabras_clave_sospechosas(self):
        """Mensaje con palabras clave sospechosas debe ser smishing"""
        mensaje = "Felicidades! Ganaste un premio. Urgente, reclama ahora tu premio gratis"
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5
        assert "palabra_clave_sospechosa" in result["reasons"]
    
    def test_mensaje_con_email_y_monto(self):
        """Mensaje con email y monto debe ser smishing"""
        mensaje = "Transferencia de $1000 USD. Contactar a winner@prize.com para reclamar"
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5
        assert any("email" in r or "monto" in r for r in result["reasons"])
    
    def test_mensaje_con_numero_codigo(self):
        """Mensaje con números/códigos sospechosos"""
        mensaje = "Tu código de verificación es 123456. Ingresa en http://verify.com"
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5
    
    def test_mensaje_spam_real_dataset_1(self):
        """Mensaje spam real del dataset"""
        mensaje = "FREE for 1st week! No1 Nokia tone 4 ur mob every week just txt NOKIA to 8077 Get txting and tell ur mates. zed POBox 36504 W45WQ norm150p/tone 16+"
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5
    
    def test_mensaje_spam_real_dataset_2(self):
        """Otro mensaje spam real del dataset"""
        mensaje = "WINNER!! As a valued network customer you have been selected to receivea £900 prize reward! To claim call 09061701461. Claim code KL341. Valid 12 hours only."
        result = classify(mensaje)
        assert result["label"] == "smishing"
        assert result["score"] >= 0.5


class TestClassifyHamMessages:
    """Tests con mensajes claramente legítimos"""
    
    def test_mensaje_simple_saludo(self):
        """Mensaje simple de saludo debe ser ham"""
        mensaje = "Hola, ¿cómo estás? Nos vemos mañana"
        result = classify(mensaje)
        assert result["label"] == "ham"
        assert result["score"] < 0.5
    
    def test_mensaje_conversacion_normal(self):
        """Conversación normal debe ser ham"""
        mensaje = "Ok, te llamo en la tarde para coordinar la reunión"
        result = classify(mensaje)
        assert result["label"] == "ham"
        assert result["score"] < 0.5
    
    def test_mensaje_ham_real_dataset_1(self):
        """Mensaje ham real del dataset"""
        mensaje = "Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got amore wat..."
        result = classify(mensaje)
        assert result["label"] == "ham"
        assert result["score"] < 0.5
    
    def test_mensaje_ham_real_dataset_2(self):
        """Otro mensaje ham real del dataset"""
        mensaje = "Ok lar... Joking wif u oni..."
        result = classify(mensaje)
        assert result["label"] == "ham"
        assert result["score"] < 0.5
    
    def test_mensaje_informativo(self):
        """Mensaje informativo legítimo"""
        mensaje = "La reunión es a las 3pm en la sala de conferencias"
        result = classify(mensaje)
        assert result["label"] == "ham"
        assert result["score"] < 0.5


class TestClassifyAmbiguous:
    """Tests con casos ambiguos"""
    
    def test_mensaje_con_numero_legitimo(self):
        """Mensaje con número pero contexto legítimo"""
        mensaje = "Mi número es 987654321, llámame cuando puedas"
        result = classify(mensaje)
        # Puede ser ham o smishing dependiendo del score
        assert result["label"] in ["smishing", "ham"]
        assert 0.0 <= result["score"] <= 1.0
    
    def test_mensaje_corto(self):
        """Mensaje muy corto"""
        mensaje = "Ok"
        result = classify(mensaje)
        assert result["label"] in ["smishing", "ham"]
        assert 0.0 <= result["score"] <= 1.0
    
    def test_mensaje_vacio(self):
        """Mensaje vacío debe manejarse correctamente"""
        result = classify("")
        assert result["label"] == "ham"
        assert result["score"] == 0.0


class TestScoreProportional:
    """Tests que verifican que el score es proporcional a los indicadores"""
    
    def test_mas_indicadores_mayor_score(self):
        """Más indicadores de smishing = mayor score"""
        mensaje_1_indicador = "Click aquí"
        mensaje_3_indicadores = "URGENTE! Ganaste $1000. Click http://premio.com"
        
        result1 = classify(mensaje_1_indicador)
        result2 = classify(mensaje_3_indicadores)
        
        assert result2["score"] > result1["score"]
    
    def test_score_incremental_con_urls(self):
        """Score aumenta con más URLs"""
        mensaje_1_url = "Visita http://ejemplo.com"
        mensaje_2_urls = "Visita http://ejemplo.com y http://otro.com"
        
        result1 = classify(mensaje_1_url)
        result2 = classify(mensaje_2_urls)
        
        assert result2["score"] >= result1["score"]
    
    def test_score_incremental_con_palabras_clave(self):
        """Score aumenta con más palabras clave sospechosas"""
        mensaje_1_palabra = "Felicidades por tu compra"
        mensaje_3_palabras = "Felicidades! Ganaste un premio gratis urgente"
        
        result1 = classify(mensaje_1_palabra)
        result2 = classify(mensaje_3_palabras)
        
        assert result2["score"] > result1["score"]


class TestAnalyzeDataset:
    """Tests para la función analizar_dataset"""
    
    def test_analizar_dataset_retorna_dict(self):
        """Verificar que analizar_dataset retorna un diccionario"""
        result = analizar_dataset()
        assert isinstance(result, dict)
    
    def test_analizar_dataset_tiene_estadisticas(self):
        """Verificar que retorna estadísticas del dataset"""
        result = analizar_dataset()
        assert "total_mensajes" in result
        assert "total_spam" in result
        assert "total_ham" in result
        assert "patrones_urls" in result
        assert "patrones_palabras_clave" in result
    
    def test_analizar_dataset_numeros_correctos(self):
        """Verificar que los números son coherentes"""
        result = analizar_dataset()
        assert result["total_mensajes"] > 0
        assert result["total_spam"] > 0
        assert result["total_ham"] > 0
        assert result["total_mensajes"] == result["total_spam"] + result["total_ham"]


class TestModelInfo:
    """Tests para la función get_model_info"""
    
    def test_get_model_info_retorna_dict(self):
        """Verificar que get_model_info retorna un diccionario"""
        result = get_model_info()
        assert isinstance(result, dict)
    
    def test_get_model_info_tiene_campos_requeridos(self):
        """Verificar que retorna información del modelo"""
        result = get_model_info()
        assert "version" in result
        assert "reglas_activas" in result
        assert "umbrales" in result
    
    def test_get_model_info_version_valida(self):
        """Verificar que la versión es una cadena válida"""
        result = get_model_info()
        assert isinstance(result["version"], str)
        assert len(result["version"]) > 0
    
    def test_get_model_info_reglas_es_lista(self):
        """Verificar que reglas_activas es una lista"""
        result = get_model_info()
        assert isinstance(result["reglas_activas"], list)
        assert len(result["reglas_activas"]) > 0
    
    def test_get_model_info_umbrales_es_dict(self):
        """Verificar que umbrales es un diccionario"""
        result = get_model_info()
        assert isinstance(result["umbrales"], dict)
        assert "clasificacion" in result["umbrales"]


class TestEvaluarModelo:
    """Tests para la función evaluar_modelo (se agregarán en fase REFACTOR)"""
    
    def test_evaluar_modelo_retorna_dict(self):
        """Verificar que evaluar_modelo retorna un diccionario"""
        result = evaluar_modelo()
        assert isinstance(result, dict)
    
    def test_evaluar_modelo_tiene_metricas(self):
        """Verificar que retorna métricas de evaluación"""
        result = evaluar_modelo()
        assert "accuracy" in result
        assert "precision" in result
        assert "recall" in result
        assert "f1_score" in result
    
    def test_evaluar_modelo_metricas_en_rango(self):
        """Verificar que las métricas están entre 0 y 1"""
        result = evaluar_modelo()
        assert 0.0 <= result["accuracy"] <= 1.0
        assert 0.0 <= result["precision"] <= 1.0
        assert 0.0 <= result["recall"] <= 1.0
        assert 0.0 <= result["f1_score"] <= 1.0
