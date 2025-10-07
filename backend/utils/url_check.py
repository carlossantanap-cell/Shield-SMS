"""
Módulo de Utilidades para Validación de URLs
Autor: Alexandro Achalma (alexandro.achalma.g@uni.pe)
Metodología: TDD (Test-Driven Development)

Funciones para detectar URLs sospechosas, acortadas y analizar riesgos.
"""

import re
from typing import Dict, Optional, Set
from urllib.parse import urlparse
from functools import lru_cache

# Dominios confiables comunes
DOMINIOS_CONFIABLES: Set[str] = {
    # Redes sociales
    'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com', 'youtube.com',
    'tiktok.com', 'snapchat.com', 'reddit.com', 'pinterest.com', 'whatsapp.com',
    
    # Tecnología y servicios
    'google.com', 'gmail.com', 'microsoft.com', 'apple.com', 'amazon.com',
    'netflix.com', 'spotify.com', 'dropbox.com', 'zoom.us', 'slack.com',
    
    # Bancos y finanzas (principales)
    'paypal.com', 'visa.com', 'mastercard.com', 'chase.com', 'bankofamerica.com',
    
    # Gobierno y educación
    'gob.pe', 'gov', 'edu', 'ac.uk', 'edu.pe',
    
    # E-commerce
    'ebay.com', 'aliexpress.com', 'mercadolibre.com', 'walmart.com',
    
    # Noticias
    'bbc.com', 'cnn.com', 'nytimes.com', 'theguardian.com', 'reuters.com'
}

# Acortadores de URL conocidos
ACORTADORES_URL: Set[str] = {
    'bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly',
    'adf.ly', 'bl.ink', 'lnkd.in', 'shorte.st', 'mcaf.ee', 'q.gs', 'po.st',
    'bc.vc', 'twitthis.com', 'u.to', 'j.mp', 'buzurl.com', 'cutt.us',
    'u.bb', 'yourls.org', 'x.co', 'prettylinkpro.com', 'scrnch.me',
    'filoops.info', 'vzturl.com', 'qr.net', '1url.com', 'tweez.me',
    'v.gd', 'tr.im', 'link.zip', 'short.link', 'tiny.cc'
}

# Patrones regex para validación
URL_PATTERN = re.compile(
    r'^(?:http|https)://[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*'
    r'(?:/[^\s]*)?$|^www\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
    r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(?:/[^\s]*)?$'
)

IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')


def validar_url(url: str) -> bool:
    """
    Valida si una cadena tiene formato de URL válido.
    
    Args:
        url: Cadena a validar
        
    Returns:
        True si es una URL válida, False en caso contrario
        
    Examples:
        >>> validar_url("https://www.google.com")
        True
        >>> validar_url("not a url")
        False
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    if not url:
        return False
    
    return bool(URL_PATTERN.match(url))


def extraer_dominio(url: str) -> str:
    """
    Extrae el dominio principal de una URL.
    
    Args:
        url: URL de la cual extraer el dominio
        
    Returns:
        Dominio extraído (ej: "google.com")
        
    Examples:
        >>> extraer_dominio("https://www.google.com/search")
        'google.com'
        >>> extraer_dominio("http://bit.ly/abc")
        'bit.ly'
    """
    if not url:
        return ""
    
    # Agregar esquema si no existe
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.netloc
        
        if not hostname:
            return ""
        
        # Remover 'www.' si existe
        if hostname.startswith('www.'):
            hostname = hostname[4:]
        
        return hostname
    except Exception:
        return ""


def es_url_acortada(url: str) -> bool:
    """
    Detecta si una URL es de un servicio acortador conocido.
    
    Args:
        url: URL a verificar
        
    Returns:
        True si es una URL acortada, False en caso contrario
        
    Examples:
        >>> es_url_acortada("http://bit.ly/abc123")
        True
        >>> es_url_acortada("https://www.google.com")
        False
    """
    if not url:
        return False
    
    dominio = extraer_dominio(url)
    return dominio in ACORTADORES_URL


def es_url_sospechosa(url: str) -> bool:
    """
    Determina si una URL es potencialmente sospechosa.
    
    Una URL se considera sospechosa si:
    - Es de un acortador de URLs
    - Contiene una dirección IP en lugar de dominio
    - No está en la lista de dominios confiables
    - Tiene patrones sospechosos en el dominio
    
    Args:
        url: URL a analizar
        
    Returns:
        True si la URL es sospechosa, False si parece confiable
        
    Examples:
        >>> es_url_sospechosa("http://bit.ly/malware")
        True
        >>> es_url_sospechosa("https://www.google.com")
        False
    """
    if not url:
        return False
    
    # URLs acortadas son sospechosas
    if es_url_acortada(url):
        return True
    
    # URLs con IP son sospechosas
    if IP_PATTERN.search(url):
        return True
    
    # Extraer dominio
    dominio = extraer_dominio(url)
    if not dominio:
        return True
    
    # Verificar si está en dominios confiables
    # Comparar con el dominio base (ej: google.com)
    partes_dominio = dominio.split('.')
    if len(partes_dominio) >= 2:
        dominio_base = '.'.join(partes_dominio[-2:])
        if dominio_base in DOMINIOS_CONFIABLES:
            return False
    
    # Verificar dominio completo
    if dominio in DOMINIOS_CONFIABLES:
        return False
    
    # Patrones sospechosos en el dominio
    patrones_sospechosos = [
        'secure', 'verify', 'account', 'login', 'signin', 'update',
        'confirm', 'banking', 'paypal', 'amazon', 'apple', 'microsoft',
        'netflix', 'facebook', 'google', 'bank', 'wallet', 'crypto'
    ]
    
    dominio_lower = dominio.lower()
    for patron in patrones_sospechosos:
        if patron in dominio_lower and dominio not in DOMINIOS_CONFIABLES:
            # Si contiene palabras de marcas conocidas pero no es el dominio oficial
            return True
    
    # Si no está en confiables y tiene características sospechosas
    # considerarlo sospechoso por defecto (enfoque conservador)
    return True


@lru_cache(maxsize=256)
def analizar_url_completo(url: str) -> Dict[str, any]:
    """
    Realiza un análisis completo de una URL y retorna un diccionario con métricas.
    
    Args:
        url: URL a analizar
        
    Returns:
        Diccionario con:
        - es_sospechosa (bool): Si la URL es sospechosa
        - es_acortada (bool): Si es una URL acortada
        - dominio (str): Dominio extraído
        - score_riesgo (float): Puntuación de riesgo (0.0-1.0)
        
    Examples:
        >>> resultado = analizar_url_completo("http://bit.ly/malware")
        >>> resultado['es_sospechosa']
        True
        >>> resultado['score_riesgo'] > 0.5
        True
    """
    if not url:
        return {
            "es_sospechosa": False,
            "es_acortada": False,
            "dominio": "",
            "score_riesgo": 0.0
        }
    
    dominio = extraer_dominio(url)
    es_acortada = es_url_acortada(url)
    es_sospechosa = es_url_sospechosa(url)
    
    # Calcular score de riesgo
    score_riesgo = 0.0
    
    if es_acortada:
        score_riesgo += 0.4
    
    if IP_PATTERN.search(url):
        score_riesgo += 0.3
    
    if es_sospechosa and not es_acortada:
        score_riesgo += 0.3
    
    # Verificar longitud del dominio (dominios muy cortos o muy largos son sospechosos)
    if dominio:
        if len(dominio) < 5 or len(dominio) > 50:
            score_riesgo += 0.1
    
    # Verificar número de subdominios (muchos subdominios es sospechoso)
    if dominio:
        num_subdominios = dominio.count('.')
        if num_subdominios > 3:
            score_riesgo += 0.2
    
    # Limitar score entre 0 y 1
    score_riesgo = min(1.0, score_riesgo)
    
    return {
        "es_sospechosa": es_sospechosa,
        "es_acortada": es_acortada,
        "dominio": dominio,
        "score_riesgo": score_riesgo
    }
