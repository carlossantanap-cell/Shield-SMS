"""
Módulo de Procesamiento de Lenguaje Natural (PLN)
Funciones para limpieza y extracción de patrones en textos SMS
Autor: Antony Lipa (antony.lipa.b@uni.pe)

Este módulo proporciona funciones optimizadas para el preprocesamiento de mensajes SMS,
incluyendo limpieza de texto, tokenización, y extracción de patrones sospechosos.
"""

import re
import string
import nltk
from typing import List, Dict, Optional, Set, Any
from functools import lru_cache

# Descargar stopwords si no están disponibles
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

from nltk.corpus import stopwords

# Cache para stopwords (optimización)
@lru_cache(maxsize=1)
def _get_stopwords() -> Set[str]:
    """
    Obtiene y cachea las stopwords en español e inglés.
    
    Returns:
        Set[str]: Conjunto de stopwords en español e inglés
    """
    stopwords_es = set(stopwords.words('spanish'))
    stopwords_en = set(stopwords.words('english'))
    return stopwords_es.union(stopwords_en)

# Palabras clave sospechosas expandidas (analizadas del dataset SMSSpamCollection)
PALABRAS_CLAVE_SOSPECHOSAS: Set[str] = {
    # Español
    'premio', 'gana', 'ganador', 'ganaste', 'click', 'urgente', 'gratis', 
    'felicidades', 'código', 'codigo', 'verificar', 'verifica', 'cuenta', 
    'banco', 'tarjeta', 'llamar', 'llama', 'contactar', 'responder',
    'oferta', 'descuento', 'promoción', 'limitado', 'ahora', 'inmediato',
    'confirmar', 'actualizar', 'bloquear', 'suspender', 'caducar',
    'contraseña', 'clave', 'pin', 'seguridad', 'acceso',
    
    # Inglés (común en dataset)
    'winner', 'won', 'win', 'free', 'urgent', 'congratulations', 'congrats',
    'prize', 'claim', 'verify', 'account', 'bank', 'card', 'credit',
    'password', 'pin', 'security', 'code', 'call', 'text', 'reply',
    'offer', 'discount', 'promotion', 'limited', 'now', 'immediately',
    'confirm', 'update', 'block', 'suspend', 'expire', 'expired',
    'guaranteed', 'cash', 'bonus', 'reward', 'gift', 'mobile',
    'txt', 'msg', 'stop', 'unsubscribe', 'opt-out', 'customer',
    'service', 'support', 'helpdesk', 'urgent', 'important', 'alert',
    'warning', 'notice', 'final', 'last', 'chance', 'opportunity'
}

# Patrones regex compilados (optimización)
EMOJI_PATTERN = re.compile(
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

URL_HTTP_PATTERN = re.compile(r'https?://[^\s]+')
URL_WWW_PATTERN = re.compile(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
URL_DOMAIN_PATTERN = re.compile(r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b')
EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
NUMBER_PATTERN = re.compile(r'\b\d{3,}\b')
MONEY_DOLLAR_PATTERN = re.compile(r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?')
MONEY_CURRENCY_PATTERN = re.compile(r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|GBP|PEN|SOL|SOLES)\b', re.IGNORECASE)
MONEY_SOLES_PATTERN = re.compile(r'S/\s*\d+(?:,\d{3})*(?:\.\d{2})?')
MONEY_POUND_PATTERN = re.compile(r'£\s*\d+(?:,\d{3})*(?:\.\d{2})?')
SPECIAL_CHARS_PATTERN = re.compile(r'[^a-záéíóúñü\s]')
WHITESPACE_PATTERN = re.compile(r'\s+')


def limpiar_texto(text: Optional[str]) -> str:
    """
    Limpia el texto eliminando puntuación, emojis, caracteres especiales,
    stopwords y normalizando espacios.
    
    Args:
        text: Texto a limpiar. Puede ser None o vacío.
        
    Returns:
        str: Texto limpio en minúsculas sin stopwords.
        
    Examples:
        >>> limpiar_texto("¡HOLA MUNDO!")
        'hola mundo'
        >>> limpiar_texto("El gato está en la casa")
        'gato casa'
        >>> limpiar_texto("")
        ''
        >>> limpiar_texto(None)
        ''
    """
    # Manejo de casos edge
    if not text or not isinstance(text, str) or not text.strip():
        return ""
    
    # Convertir a minúsculas
    texto = text.lower()
    
    # Eliminar emojis
    texto = EMOJI_PATTERN.sub('', texto)
    
    # Eliminar signos de puntuación
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    
    # Eliminar caracteres especiales (mantener solo letras, números y espacios)
    texto = SPECIAL_CHARS_PATTERN.sub('', texto)
    
    # Tokenizar y eliminar stopwords
    palabras = texto.split()
    stopwords_set = _get_stopwords()
    palabras_filtradas = [palabra for palabra in palabras if palabra and palabra not in stopwords_set]
    
    # Unir palabras y normalizar espacios
    texto_limpio = ' '.join(palabras_filtradas)
    texto_limpio = WHITESPACE_PATTERN.sub(' ', texto_limpio).strip()
    
    return texto_limpio


def tokenizar(text: Optional[str]) -> List[str]:
    """
    Divide el texto en tokens/palabras.
    
    Args:
        text: Texto a tokenizar. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de tokens.
        
    Examples:
        >>> tokenizar("hola mundo")
        ['hola', 'mundo']
        >>> tokenizar("hola, mundo!")
        ['hola', 'mundo']
        >>> tokenizar("")
        []
        >>> tokenizar(None)
        []
    """
    # Manejo de casos edge
    if not text or not isinstance(text, str) or not text.strip():
        return []
    
    # Limpiar puntuación básica y dividir por espacios
    texto = text.translate(str.maketrans('', '', string.punctuation))
    tokens = texto.split()
    
    return [token for token in tokens if token]


def extraer_urls(text: Optional[str]) -> List[str]:
    """
    Extrae URLs del texto (http://, https://, www., dominios).
    
    Args:
        text: Texto del cual extraer URLs. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de URLs encontradas.
        
    Examples:
        >>> extraer_urls("Visita http://ejemplo.com")
        ['http://ejemplo.com']
        >>> extraer_urls("Visita www.ejemplo.com")
        ['www.ejemplo.com']
        >>> extraer_urls("Sin URLs")
        []
    """
    if not text or not isinstance(text, str):
        return []
    
    urls: List[str] = []
    
    # Buscar URLs con protocolo
    urls.extend(URL_HTTP_PATTERN.findall(text))
    
    # Buscar URLs con www
    urls.extend(URL_WWW_PATTERN.findall(text))
    
    # Buscar dominios sin protocolo
    dominios_potenciales = URL_DOMAIN_PATTERN.findall(text)
    
    for dominio in dominios_potenciales:
        # Verificar que no esté ya incluido
        if not any(dominio in url for url in urls):
            urls.append(dominio)
    
    return urls


def extraer_emails(text: Optional[str]) -> List[str]:
    """
    Extrae direcciones de email del texto.
    
    Args:
        text: Texto del cual extraer emails. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de emails encontrados.
        
    Examples:
        >>> extraer_emails("Contacta a usuario@ejemplo.com")
        ['usuario@ejemplo.com']
        >>> extraer_emails("Sin emails")
        []
    """
    if not text or not isinstance(text, str):
        return []
    
    return EMAIL_PATTERN.findall(text)


def extraer_numeros(text: Optional[str]) -> List[str]:
    """
    Extrae números del texto (teléfonos, códigos, etc.).
    
    Args:
        text: Texto del cual extraer números. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de números encontrados (secuencias de 3+ dígitos).
        
    Examples:
        >>> extraer_numeros("Llama al 123456789")
        ['123456789']
        >>> extraer_numeros("Código: 12345")
        ['12345']
        >>> extraer_numeros("Sin números")
        []
    """
    if not text or not isinstance(text, str):
        return []
    
    return NUMBER_PATTERN.findall(text)


def extraer_montos(text: Optional[str]) -> List[str]:
    """
    Extrae montos de dinero del texto ($100, 100 USD, S/ 100, £100, etc.).
    
    Args:
        text: Texto del cual extraer montos. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de montos encontrados.
        
    Examples:
        >>> extraer_montos("Ganaste $100")
        ['$100']
        >>> extraer_montos("Precio: 100 USD")
        ['100 USD']
        >>> extraer_montos("Sin montos")
        []
    """
    if not text or not isinstance(text, str):
        return []
    
    montos: List[str] = []
    
    # Buscar diferentes formatos de montos
    montos.extend(MONEY_DOLLAR_PATTERN.findall(text))
    montos.extend(MONEY_CURRENCY_PATTERN.findall(text))
    montos.extend(MONEY_SOLES_PATTERN.findall(text))
    montos.extend(MONEY_POUND_PATTERN.findall(text))
    
    return montos


def extraer_palabras_clave(text: Optional[str]) -> List[str]:
    """
    Extrae palabras clave sospechosas del texto (indicadores de smishing).
    
    Args:
        text: Texto del cual extraer palabras clave. Puede ser None o vacío.
        
    Returns:
        List[str]: Lista de palabras clave sospechosas encontradas.
        
    Examples:
        >>> extraer_palabras_clave("Felicidades ganaste un premio")
        ['felicidades', 'ganaste', 'premio']
        >>> extraer_palabras_clave("URGENTE: verifica tu cuenta")
        ['urgente', 'verifica', 'cuenta']
    """
    if not text or not isinstance(text, str):
        return []
    
    texto_lower = text.lower()
    palabras_encontradas: List[str] = []
    
    for palabra_clave in PALABRAS_CLAVE_SOSPECHOSAS:
        # Buscar palabra completa (con límites de palabra)
        if re.search(r'\b' + re.escape(palabra_clave) + r'\b', texto_lower):
            palabras_encontradas.append(palabra_clave)
    
    return palabras_encontradas


def preprocesar_completo(text: Optional[str]) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de preprocesamiento.
    
    Aplica todas las funciones de preprocesamiento en un solo paso,
    retornando un diccionario con todos los resultados.
    
    Args:
        text: Texto a preprocesar. Puede ser None o vacío.
        
    Returns:
        Dict[str, Any]: Diccionario con los siguientes campos:
            - texto_limpio (str): Texto limpio sin stopwords
            - tokens (List[str]): Lista de tokens
            - urls (List[str]): URLs encontradas
            - emails (List[str]): Emails encontrados
            - numeros (List[str]): Números encontrados
            - montos (List[str]): Montos de dinero encontrados
            - palabras_clave (List[str]): Palabras clave sospechosas
            
    Examples:
        >>> resultado = preprocesar_completo("¡GANASTE $1000! Visita premio.com")
        >>> resultado['palabras_clave']
        ['ganaste']
        >>> len(resultado['urls']) > 0
        True
        >>> len(resultado['montos']) > 0
        True
    """
    # Manejo de casos edge
    if not text or not isinstance(text, str):
        return {
            'texto_limpio': '',
            'tokens': [],
            'urls': [],
            'emails': [],
            'numeros': [],
            'montos': [],
            'palabras_clave': []
        }
    
    resultado: Dict[str, Any] = {
        'texto_limpio': limpiar_texto(text),
        'tokens': tokenizar(text),
        'urls': extraer_urls(text),
        'emails': extraer_emails(text),
        'numeros': extraer_numeros(text),
        'montos': extraer_montos(text),
        'palabras_clave': extraer_palabras_clave(text)
    }
    
    return resultado
