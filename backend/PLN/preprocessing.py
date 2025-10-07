"""
Módulo de Procesamiento de Lenguaje Natural (PLN)
Funciones para limpieza y extracción de patrones en textos SMS
Autor: Antony Lipa (antony.lipa.b@uni.pe)
"""

import re
import string
import nltk
from typing import List, Dict

# Descargar stopwords si no están disponibles
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

# Cargar stopwords en español e inglés
STOPWORDS_ES = set(stopwords.words('spanish'))
STOPWORDS_EN = set(stopwords.words('english'))
STOPWORDS = STOPWORDS_ES.union(STOPWORDS_EN)

# Palabras clave sospechosas comunes en smishing
PALABRAS_CLAVE_SOSPECHOSAS = {
    'premio', 'gana', 'ganador', 'ganaste', 'click', 'urgente', 'gratis', 
    'felicidades', 'código', 'codigo', 'verificar', 'verifica', 'cuenta', 
    'banco', 'tarjeta', 'winner', 'won', 'free', 'urgent', 'congratulations',
    'prize', 'claim', 'verify', 'account', 'bank', 'card', 'credit',
    'password', 'contraseña', 'pin', 'código de seguridad', 'security code'
}


def limpiar_texto(text: str) -> str:
    """
    Limpia el texto eliminando puntuación, emojis, caracteres especiales,
    stopwords y normalizando espacios.
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto limpio en minúsculas sin stopwords
    """
    if not text or not text.strip():
        return ""
    
    # Convertir a minúsculas
    texto = text.lower()
    
    # Eliminar emojis (rangos Unicode comunes)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        "\U0001F680-\U0001F6FF"  # transporte & símbolos de mapa
        "\U0001F1E0-\U0001F1FF"  # banderas
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    texto = emoji_pattern.sub(r'', texto)
    
    # Eliminar signos de puntuación
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    
    # Eliminar caracteres especiales (mantener solo letras, números y espacios)
    texto = re.sub(r'[^a-záéíóúñü\s]', '', texto)
    
    # Tokenizar y eliminar stopwords
    palabras = texto.split()
    palabras_filtradas = [palabra for palabra in palabras if palabra not in STOPWORDS]
    
    # Unir palabras y normalizar espacios
    texto_limpio = ' '.join(palabras_filtradas)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    
    return texto_limpio


def tokenizar(text: str) -> List[str]:
    """
    Divide el texto en tokens/palabras.
    
    Args:
        text: Texto a tokenizar
        
    Returns:
        Lista de tokens
    """
    if not text or not text.strip():
        return []
    
    # Limpiar puntuación básica y dividir por espacios
    texto = text.translate(str.maketrans('', '', string.punctuation))
    tokens = texto.split()
    
    return [token for token in tokens if token]


def extraer_urls(text: str) -> List[str]:
    """
    Extrae URLs del texto.
    
    Args:
        text: Texto del cual extraer URLs
        
    Returns:
        Lista de URLs encontradas
    """
    if not text:
        return []
    
    urls = []
    
    # Patrón para URLs con protocolo (http, https)
    patron_http = r'https?://[^\s]+'
    urls.extend(re.findall(patron_http, text))
    
    # Patrón para URLs con www
    patron_www = r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    urls.extend(re.findall(patron_www, text))
    
    # Patrón para dominios sin protocolo (ejemplo.com)
    # Buscar palabras que contengan un punto y terminen en TLD común
    patron_dominio = r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b'
    dominios_potenciales = re.findall(patron_dominio, text)
    
    for dominio in dominios_potenciales:
        # Verificar que no esté ya incluido en una URL con protocolo o www
        ya_incluido = False
        for url in urls:
            if dominio in url:
                ya_incluido = True
                break
        
        if not ya_incluido:
            urls.append(dominio)
    
    return urls


def extraer_emails(text: str) -> List[str]:
    """
    Extrae direcciones de email del texto.
    
    Args:
        text: Texto del cual extraer emails
        
    Returns:
        Lista de emails encontrados
    """
    if not text:
        return []
    
    # Patrón para emails
    patron_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    emails = re.findall(patron_email, text)
    
    return emails


def extraer_numeros(text: str) -> List[str]:
    """
    Extrae números del texto (teléfonos, códigos, etc.).
    
    Args:
        text: Texto del cual extraer números
        
    Returns:
        Lista de números encontrados
    """
    if not text:
        return []
    
    # Patrón para números (secuencias de 3 o más dígitos)
    patron_numeros = r'\b\d{3,}\b'
    
    numeros = re.findall(patron_numeros, text)
    
    return numeros


def extraer_montos(text: str) -> List[str]:
    """
    Extrae montos de dinero del texto.
    
    Args:
        text: Texto del cual extraer montos
        
    Returns:
        Lista de montos encontrados
    """
    if not text:
        return []
    
    montos = []
    
    # Patrón para montos con símbolo de dólar
    patron_dolar = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    montos.extend(re.findall(patron_dolar, text))
    
    # Patrón para montos con USD, EUR, etc.
    patron_moneda = r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|PEN|SOL|SOLES)\b'
    montos.extend(re.findall(patron_moneda, text, re.IGNORECASE))
    
    # Patrón para montos con S/
    patron_soles = r'S/\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    montos.extend(re.findall(patron_soles, text))
    
    # Patrón para símbolo de libra esterlina
    patron_libra = r'£\s*\d+(?:,\d{3})*(?:\.\d{2})?'
    montos.extend(re.findall(patron_libra, text))
    
    return montos


def extraer_palabras_clave(text: str) -> List[str]:
    """
    Extrae palabras clave sospechosas del texto.
    
    Args:
        text: Texto del cual extraer palabras clave
        
    Returns:
        Lista de palabras clave sospechosas encontradas
    """
    if not text:
        return []
    
    texto_lower = text.lower()
    palabras_encontradas = []
    
    for palabra_clave in PALABRAS_CLAVE_SOSPECHOSAS:
        if palabra_clave in texto_lower:
            palabras_encontradas.append(palabra_clave)
    
    return palabras_encontradas


def preprocesar_completo(text: str) -> Dict[str, any]:
    """
    Ejecuta el pipeline completo de preprocesamiento.
    
    Args:
        text: Texto a preprocesar
        
    Returns:
        Diccionario con todos los resultados del preprocesamiento
    """
    resultado = {
        'texto_limpio': limpiar_texto(text),
        'tokens': tokenizar(text),
        'urls': extraer_urls(text),
        'emails': extraer_emails(text),
        'numeros': extraer_numeros(text),
        'montos': extraer_montos(text),
        'palabras_clave': extraer_palabras_clave(text)
    }
    
    return resultado
