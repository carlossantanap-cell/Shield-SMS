
"""
Modelo ML basado en Reglas para Detección de Smishing
Implementación: Juan Gonzales (j.gonzales.avendano@uni.pe)
Metodología: TDD (Test-Driven Development)

Sistema de puntuación optimizado basado en análisis del dataset SMSSpamCollection:

Reglas principales (basadas en indicadores):
- URLs detectadas: +0.35 por cada una (alta correlación con spam)
- Palabras clave sospechosas: +0.18 por cada una
- Emails detectados: +0.12 por cada uno
- Números/códigos: +0.08 por cada uno
- Montos detectados: +0.15 por cada uno

Reglas adicionales (basadas en análisis estadístico):
- Longitud del mensaje: +0.15 si > 120 caracteres (spam promedio: 138 chars)
- Ratio de mayúsculas: +0.20 si > 15% (spam promedio: 11%, ham: 5.8%)
- Múltiples exclamaciones: +0.15 si >= 2 signos (16% spam vs 3.8% ham)
- Palabras de urgencia: +0.12 si detectadas (35% spam vs 11% ham)
- Combinación de indicadores: +0.10 bonus si >= 3 indicadores diferentes

Penalizaciones:
- Mensaje muy corto: -0.15 si < 10 caracteres sin indicadores

Umbral de clasificación: score >= 0.55 → smishing (ajustado para reducir falsos positivos)
"""

from typing import Dict, List, Any, Optional, Set
import os
import sys
import re
from pathlib import Path

# Importar funciones del módulo PLN
sys.path.insert(0, str(Path(__file__).parent.parent))
from PLN.preprocessing import (
    preprocesar_completo,
    extraer_urls,
    extraer_emails,
    extraer_numeros,
    extraer_montos,
    extraer_palabras_clave
)

# Configuración del modelo
MODEL_VERSION = "2.0.0"
CLASSIFICATION_THRESHOLD = 0.55

# Pesos optimizados de las reglas principales
WEIGHTS = {
    "url": 0.35,
    "palabra_clave": 0.18,
    "email": 0.12,
    "numero": 0.08,
    "monto": 0.15
}

# Pesos de reglas adicionales
ADDITIONAL_WEIGHTS = {
    "longitud_sospechosa": 0.15,
    "mayusculas_excesivas": 0.20,
    "multiples_exclamaciones": 0.15,
    "urgencia": 0.12,
    "combinacion_indicadores": 0.10,
    "mensaje_muy_corto": -0.15
}

# Umbrales para reglas adicionales
THRESHOLDS = {
    "longitud_minima_spam": 120,
    "ratio_mayusculas": 0.15,
    "min_exclamaciones": 2,
    "longitud_muy_corta": 10,
    "min_indicadores_combinacion": 3
}

# Palabras de urgencia
URGENCY_WORDS: Set[str] = {
    'urgent', 'urgente', 'now', 'ahora', 'immediately', 'inmediatamente',
    'hurry', 'apurate', 'quick', 'rapido', 'asap', 'limited', 'limitado',
    'expires', 'expira', 'today', 'hoy', 'tonight', 'esta noche'
}


def _detectar_urgencia(text: str) -> bool:
    """
    Detecta si el mensaje contiene palabras de urgencia.
    
    Args:
        text: Mensaje de texto
        
    Returns:
        True si contiene palabras de urgencia, False en caso contrario
    """
    text_lower = text.lower()
    return any(word in text_lower for word in URGENCY_WORDS)


def _calcular_ratio_mayusculas(text: str) -> float:
    """
    Calcula el ratio de letras mayúsculas en el texto.
    
    Args:
        text: Mensaje de texto
        
    Returns:
        Ratio de mayúsculas (0.0 a 1.0)
    """
    if not text:
        return 0.0
    
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    
    upper_count = sum(1 for c in letters if c.isupper())
    return upper_count / len(letters)


def classify(text: str) -> Dict[str, Any]:
    """
    Clasifica un mensaje de texto como 'smishing' o 'ham' usando un sistema
    de reglas optimizado basado en análisis estadístico del dataset.
    
    Args:
        text: Mensaje de texto a clasificar
        
    Returns:
        Dict con:
        - label: "smishing" o "ham"
        - score: float entre 0.0 y 1.0 (confianza de la clasificación)
        - reasons: lista de razones de la clasificación
        
    Examples:
        >>> result = classify("URGENT! Win $1000 now: http://bit.ly/prize")
        >>> result['label']
        'smishing'
        >>> result['score'] > 0.5
        True
    """
    if not text or text.strip() == "":
        return {
            "label": "ham",
            "score": 0.0,
            "reasons": []
        }
    
    # Preprocesar el texto y extraer características principales
    urls = extraer_urls(text)
    emails = extraer_emails(text)
    numeros = extraer_numeros(text)
    montos = extraer_montos(text)
    palabras_clave = extraer_palabras_clave(text)
    
    # Calcular score basado en indicadores principales
    score = 0.0
    reasons = []
    num_indicadores = 0
    
    # URLs detectadas
    if urls:
        score += len(urls) * WEIGHTS["url"]
        reasons.append("url_detectada")
        num_indicadores += 1
    
    # Palabras clave sospechosas
    if palabras_clave:
        score += len(palabras_clave) * WEIGHTS["palabra_clave"]
        reasons.append("palabra_clave_sospechosa")
        num_indicadores += 1
    
    # Emails detectados
    if emails:
        score += len(emails) * WEIGHTS["email"]
        reasons.append("email_detectado")
        num_indicadores += 1
    
    # Números/códigos detectados
    if numeros:
        score += len(numeros) * WEIGHTS["numero"]
        reasons.append("numero_detectado")
        num_indicadores += 1
    
    # Montos detectados
    if montos:
        score += len(montos) * WEIGHTS["monto"]
        reasons.append("monto_detectado")
        num_indicadores += 1
    
    # === REGLAS ADICIONALES (basadas en análisis estadístico) ===
    
    # Longitud del mensaje (spam promedio: 138 chars, ham: 71 chars)
    if len(text) > THRESHOLDS["longitud_minima_spam"]:
        score += ADDITIONAL_WEIGHTS["longitud_sospechosa"]
        reasons.append("longitud_sospechosa")
    
    # Ratio de mayúsculas (spam: 11%, ham: 5.8%)
    ratio_mayusculas = _calcular_ratio_mayusculas(text)
    if ratio_mayusculas > THRESHOLDS["ratio_mayusculas"]:
        score += ADDITIONAL_WEIGHTS["mayusculas_excesivas"]
        reasons.append("mayusculas_excesivas")
    
    # Múltiples signos de exclamación (16% spam vs 3.8% ham)
    exclamation_count = text.count('!')
    if exclamation_count >= THRESHOLDS["min_exclamaciones"]:
        score += ADDITIONAL_WEIGHTS["multiples_exclamaciones"]
        reasons.append("multiples_exclamaciones")
    
    # Palabras de urgencia (35% spam vs 11% ham)
    if _detectar_urgencia(text):
        score += ADDITIONAL_WEIGHTS["urgencia"]
        reasons.append("urgencia_detectada")
    
    # Bonus por combinación de múltiples indicadores
    if num_indicadores >= THRESHOLDS["min_indicadores_combinacion"]:
        score += ADDITIONAL_WEIGHTS["combinacion_indicadores"]
        reasons.append("combinacion_indicadores")
    
    # Penalización por mensaje muy corto sin indicadores
    if len(text) < THRESHOLDS["longitud_muy_corta"] and num_indicadores == 0:
        score += ADDITIONAL_WEIGHTS["mensaje_muy_corto"]  # Es negativo
        reasons.append("mensaje_muy_corto")
    
    # Limitar score al rango [0.0, 1.0]
    score = max(0.0, min(score, 1.0))
    
    # Clasificar según umbral optimizado
    label = "smishing" if score >= CLASSIFICATION_THRESHOLD else "ham"
    
    return {
        "label": label,
        "score": score,
        "reasons": reasons
    }


def analizar_dataset() -> Dict[str, Any]:
    """
    Analiza el dataset completo y retorna estadísticas de patrones encontrados.
    
    Returns:
        Dict con estadísticas del dataset:
        - total_mensajes: número total de mensajes
        - total_spam: número de mensajes spam
        - total_ham: número de mensajes ham
        - patrones_urls: número de mensajes con URLs
        - patrones_palabras_clave: número de mensajes con palabras clave
        - patrones_emails: número de mensajes con emails
        - patrones_numeros: número de mensajes con números
        - patrones_montos: número de mensajes con montos
    """
    # Ruta al dataset
    dataset_path = Path(__file__).parent.parent / "data" / "dataset.csv"
    
    if not dataset_path.exists():
        return {
            "error": "Dataset no encontrado",
            "total_mensajes": 0,
            "total_spam": 0,
            "total_ham": 0
        }
    
    # Contadores
    total_mensajes = 0
    total_spam = 0
    total_ham = 0
    patrones_urls = 0
    patrones_palabras_clave = 0
    patrones_emails = 0
    patrones_numeros = 0
    patrones_montos = 0
    
    # Leer y analizar dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t', 1)
            if len(parts) != 2:
                continue
            
            label, text = parts
            total_mensajes += 1
            
            if label == "spam":
                total_spam += 1
            else:
                total_ham += 1
            
            # Analizar patrones
            if extraer_urls(text):
                patrones_urls += 1
            if extraer_palabras_clave(text):
                patrones_palabras_clave += 1
            if extraer_emails(text):
                patrones_emails += 1
            if extraer_numeros(text):
                patrones_numeros += 1
            if extraer_montos(text):
                patrones_montos += 1
    
    return {
        "total_mensajes": total_mensajes,
        "total_spam": total_spam,
        "total_ham": total_ham,
        "patrones_urls": patrones_urls,
        "patrones_palabras_clave": patrones_palabras_clave,
        "patrones_emails": patrones_emails,
        "patrones_numeros": patrones_numeros,
        "patrones_montos": patrones_montos
    }


def get_model_info() -> Dict[str, Any]:
    """
    Retorna información completa del modelo (versión, reglas activas, umbrales, pesos).
    
    Returns:
        Dict con información del modelo:
        - version: versión del modelo
        - reglas_activas: lista de reglas activas (principales y adicionales)
        - umbrales: diccionario con todos los umbrales de clasificación
        - pesos: diccionario con pesos de reglas principales
        - pesos_adicionales: diccionario con pesos de reglas adicionales
        - descripcion: descripción del modelo
    """
    return {
        "version": MODEL_VERSION,
        "reglas_activas": [
            # Reglas principales
            "deteccion_urls",
            "deteccion_palabras_clave",
            "deteccion_emails",
            "deteccion_numeros",
            "deteccion_montos",
            # Reglas adicionales
            "analisis_longitud",
            "analisis_mayusculas",
            "deteccion_exclamaciones",
            "deteccion_urgencia",
            "combinacion_indicadores",
            "penalizacion_mensajes_cortos"
        ],
        "umbrales": {
            "clasificacion": CLASSIFICATION_THRESHOLD,
            **THRESHOLDS
        },
        "pesos": WEIGHTS,
        "pesos_adicionales": ADDITIONAL_WEIGHTS,
        "descripcion": "Modelo basado en reglas optimizado con análisis estadístico del dataset SMSSpamCollection"
    }


def evaluar_modelo() -> Dict[str, float]:
    """
    Evalúa el modelo contra el dataset y retorna métricas de rendimiento.
    
    Returns:
        Dict con métricas:
        - accuracy: precisión general
        - precision: precisión para clase spam
        - recall: recall para clase spam
        - f1_score: F1-score
        - total_evaluados: número total de mens ajes evaluados
    """
    # Ruta al dataset
    dataset_path = Path(__file__).parent.parent / "data" / "dataset.csv"
    
    if not dataset_path.exists():
        return {
            "error": "Dataset no encontrado",
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0
        }
    
    # Contadores para métricas
    true_positives = 0  # spam correctamente clasificado como spam
    true_negatives = 0  # ham correctamente clasificado como ham
    false_positives = 0  # ham incorrectamente clasificado como spam
    false_negatives = 0  # spam incorrectamente clasificado como ham
    total = 0
    
    # Evaluar cada mensaje del dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t', 1)
            if len(parts) != 2:
                continue
            
            true_label, text = parts
            total += 1
            
            # Clasificar mensaje
            result = classify(text)
            predicted_label = result["label"]
            
            # Convertir labels para comparación
            true_is_spam = (true_label == "spam")
            predicted_is_spam = (predicted_label == "smishing")
            
            # Actualizar contadores
            if true_is_spam and predicted_is_spam:
                true_positives += 1
            elif not true_is_spam and not predicted_is_spam:
                true_negatives += 1
            elif not true_is_spam and predicted_is_spam:
                false_positives += 1
            elif true_is_spam and not predicted_is_spam:
                false_negatives += 1
    
    # Calcular métricas
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0.0
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "total_evaluados": total,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }
