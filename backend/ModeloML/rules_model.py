
"""
Modelo ML basado en Reglas para Detección de Smishing
Implementación: Juan Gonzales (j.gonzales.avendano@uni.pe)
Metodología: TDD (Test-Driven Development)

Sistema de puntuación basado en indicadores de smishing:
- URLs detectadas: +0.3 por cada una
- Palabras clave sospechosas: +0.2 por cada una
- Emails detectados: +0.15 por cada uno
- Números/códigos: +0.1 por cada uno
- Montos detectados: +0.15 por cada uno
- Umbral de clasificación: score >= 0.5 → smishing
"""

from typing import Dict, List, Any, Optional
import os
import sys
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
MODEL_VERSION = "1.0.0"
CLASSIFICATION_THRESHOLD = 0.5

# Pesos de las reglas
WEIGHTS = {
    "url": 0.3,
    "palabra_clave": 0.2,
    "email": 0.15,
    "numero": 0.1,
    "monto": 0.15
}


def classify(text: str) -> Dict[str, Any]:
    """
    Clasifica un mensaje de texto como 'smishing' o 'ham'.
    
    Args:
        text: Mensaje de texto a clasificar
        
    Returns:
        Dict con:
        - label: "smishing" o "ham"
        - score: float entre 0.0 y 1.0 (confianza de la clasificación)
        - reasons: lista de razones de la clasificación
    """
    if not text or text.strip() == "":
        return {
            "label": "ham",
            "score": 0.0,
            "reasons": []
        }
    
    # Preprocesar el texto y extraer características
    urls = extraer_urls(text)
    emails = extraer_emails(text)
    numeros = extraer_numeros(text)
    montos = extraer_montos(text)
    palabras_clave = extraer_palabras_clave(text)
    
    # Calcular score basado en indicadores
    score = 0.0
    reasons = []
    
    # URLs detectadas
    if urls:
        score += len(urls) * WEIGHTS["url"]
        reasons.append("url_detectada")
    
    # Palabras clave sospechosas
    if palabras_clave:
        score += len(palabras_clave) * WEIGHTS["palabra_clave"]
        reasons.append("palabra_clave_sospechosa")
    
    # Emails detectados
    if emails:
        score += len(emails) * WEIGHTS["email"]
        reasons.append("email_detectado")
    
    # Números/códigos detectados
    if numeros:
        score += len(numeros) * WEIGHTS["numero"]
        reasons.append("numero_detectado")
    
    # Montos detectados
    if montos:
        score += len(montos) * WEIGHTS["monto"]
        reasons.append("monto_detectado")
    
    # Limitar score a 1.0
    score = min(score, 1.0)
    
    # Clasificar según umbral
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
    Retorna información del modelo (versión, reglas activas, umbrales).
    
    Returns:
        Dict con información del modelo:
        - version: versión del modelo
        - reglas_activas: lista de reglas activas
        - umbrales: diccionario con umbrales de clasificación
        - pesos: diccionario con pesos de cada regla
    """
    return {
        "version": MODEL_VERSION,
        "reglas_activas": [
            "deteccion_urls",
            "deteccion_palabras_clave",
            "deteccion_emails",
            "deteccion_numeros",
            "deteccion_montos"
        ],
        "umbrales": {
            "clasificacion": CLASSIFICATION_THRESHOLD
        },
        "pesos": WEIGHTS
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
