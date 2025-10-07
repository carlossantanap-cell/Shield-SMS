"""
Tests para el módulo PLN (Procesamiento de Lenguaje Natural)
Metodología TDD - FASE REFACTOR
Autor: Antony Lipa (antony.lipa.b@uni.pe)
"""

import pytest
import time
from backend.PLN.preprocessing import (
    limpiar_texto,
    tokenizar,
    extraer_urls,
    extraer_emails,
    extraer_numeros,
    extraer_montos,
    extraer_palabras_clave,
    preprocesar_completo
)


class TestLimpiarTexto:
    """Tests para la función limpiar_texto"""
    
    def test_convertir_minusculas(self):
        texto = "HOLA MUNDO"
        resultado = limpiar_texto(texto)
        assert resultado == "hola mundo"
    
    def test_eliminar_puntuacion(self):
        texto = "¡Hola! ¿Cómo estás? Bien, gracias."
        resultado = limpiar_texto(texto)
        assert "!" not in resultado
        assert "?" not in resultado
        assert "," not in resultado
        assert "." not in resultado
    
    def test_eliminar_emojis(self):
        texto = "Felicidades 🎉🎊 ganaste un premio 🏆"
        resultado = limpiar_texto(texto)
        assert "🎉" not in resultado
        assert "🎊" not in resultado
        assert "🏆" not in resultado
    
    def test_eliminar_caracteres_especiales(self):
        texto = "Texto con @#$% caracteres especiales"
        resultado = limpiar_texto(texto)
        assert "@" not in resultado
        assert "#" not in resultado
        assert "$" not in resultado
        assert "%" not in resultado
    
    def test_eliminar_stopwords_espanol(self):
        texto = "el gato está en la casa"
        resultado = limpiar_texto(texto)
        # Stopwords comunes en español: el, en, la
        assert "el" not in resultado.split()
        assert "en" not in resultado.split()
        assert "la" not in resultado.split()
        assert "gato" in resultado
        assert "casa" in resultado
    
    def test_eliminar_stopwords_ingles(self):
        texto = "the cat is on the table"
        resultado = limpiar_texto(texto)
        # Stopwords comunes en inglés: the, is, on
        assert "the" not in resultado.split()
        assert "is" not in resultado.split()
        assert "on" not in resultado.split()
        assert "cat" in resultado
        assert "table" in resultado
    
    def test_normalizar_espacios(self):
        texto = "texto   con    espacios     múltiples"
        resultado = limpiar_texto(texto)
        assert "  " not in resultado
        assert resultado == "texto espacios múltiples"
    
    def test_texto_vacio(self):
        resultado = limpiar_texto("")
        assert resultado == ""
    
    def test_texto_solo_espacios(self):
        resultado = limpiar_texto("     ")
        assert resultado == ""
    
    def test_texto_none(self):
        """Test caso edge: texto None"""
        resultado = limpiar_texto(None)
        assert resultado == ""
    
    def test_texto_solo_emojis(self):
        """Test caso edge: texto solo con emojis"""
        resultado = limpiar_texto("🎉🎊🏆")
        assert resultado == ""
    
    def test_texto_solo_numeros(self):
        """Test caso edge: texto solo con números - se eliminan caracteres especiales"""
        resultado = limpiar_texto("123 456 789")
        # Los números se mantienen pero sin caracteres especiales
        assert isinstance(resultado, str)


class TestTokenizar:
    """Tests para la función tokenizar"""
    
    def test_tokenizar_texto_simple(self):
        texto = "hola mundo"
        tokens = tokenizar(texto)
        assert tokens == ["hola", "mundo"]
    
    def test_tokenizar_texto_con_puntuacion(self):
        texto = "hola, mundo!"
        tokens = tokenizar(texto)
        assert "hola" in tokens
        assert "mundo" in tokens
    
    def test_tokenizar_texto_vacio(self):
        tokens = tokenizar("")
        assert tokens == []
    
    def test_tokenizar_texto_largo(self):
        texto = "este es un texto largo con muchas palabras para tokenizar"
        tokens = tokenizar(texto)
        assert len(tokens) == 10
    
    def test_tokenizar_none(self):
        """Test caso edge: texto None"""
        tokens = tokenizar(None)
        assert tokens == []
    
    def test_tokenizar_solo_espacios(self):
        """Test caso edge: solo espacios"""
        tokens = tokenizar("     ")
        assert tokens == []


class TestExtraerUrls:
    """Tests para la función extraer_urls"""
    
    def test_extraer_url_http(self):
        texto = "Visita http://ejemplo.com para más info"
        urls = extraer_urls(texto)
        assert "http://ejemplo.com" in urls
    
    def test_extraer_url_https(self):
        texto = "Visita https://ejemplo.com para más info"
        urls = extraer_urls(texto)
        assert "https://ejemplo.com" in urls
    
    def test_extraer_url_www(self):
        texto = "Visita www.ejemplo.com para más info"
        urls = extraer_urls(texto)
        assert "www.ejemplo.com" in urls
    
    def test_extraer_url_sin_protocolo(self):
        texto = "Visita ejemplo.com para más info"
        urls = extraer_urls(texto)
        assert "ejemplo.com" in urls
    
    def test_extraer_multiples_urls(self):
        texto = "Visita http://ejemplo1.com y https://ejemplo2.com"
        urls = extraer_urls(texto)
        assert len(urls) == 2
    
    def test_sin_urls(self):
        texto = "Este texto no tiene URLs"
        urls = extraer_urls(texto)
        assert urls == []
    
    def test_extraer_urls_none(self):
        """Test caso edge: texto None"""
        urls = extraer_urls(None)
        assert urls == []


class TestExtraerEmails:
    """Tests para la función extraer_emails"""
    
    def test_extraer_email_simple(self):
        texto = "Contacta a usuario@ejemplo.com"
        emails = extraer_emails(texto)
        assert "usuario@ejemplo.com" in emails
    
    def test_extraer_email_con_numeros(self):
        texto = "Contacta a usuario123@ejemplo.com"
        emails = extraer_emails(texto)
        assert "usuario123@ejemplo.com" in emails
    
    def test_extraer_multiples_emails(self):
        texto = "Contacta a user1@ejemplo.com o user2@ejemplo.com"
        emails = extraer_emails(texto)
        assert len(emails) == 2
    
    def test_sin_emails(self):
        texto = "Este texto no tiene emails"
        emails = extraer_emails(texto)
        assert emails == []
    
    def test_extraer_emails_none(self):
        """Test caso edge: texto None"""
        emails = extraer_emails(None)
        assert emails == []


class TestExtraerNumeros:
    """Tests para la función extraer_numeros"""
    
    def test_extraer_numero_simple(self):
        texto = "Llama al 123456789"
        numeros = extraer_numeros(texto)
        assert "123456789" in numeros
    
    def test_extraer_numero_telefono(self):
        texto = "Llama al +51 987654321"
        numeros = extraer_numeros(texto)
        assert any("987654321" in num for num in numeros)
    
    def test_extraer_codigo(self):
        texto = "Tu código es 12345"
        numeros = extraer_numeros(texto)
        assert "12345" in numeros
    
    def test_extraer_multiples_numeros(self):
        texto = "Códigos: 123, 456, 789"
        numeros = extraer_numeros(texto)
        assert len(numeros) >= 3
    
    def test_sin_numeros(self):
        texto = "Este texto no tiene números"
        numeros = extraer_numeros(texto)
        assert numeros == []
    
    def test_extraer_numeros_none(self):
        """Test caso edge: texto None"""
        numeros = extraer_numeros(None)
        assert numeros == []


class TestExtraerMontos:
    """Tests para la función extraer_montos"""
    
    def test_extraer_monto_con_simbolo_dolar(self):
        texto = "Ganaste $100"
        montos = extraer_montos(texto)
        assert any("100" in str(monto) for monto in montos)
    
    def test_extraer_monto_con_usd(self):
        texto = "Ganaste 100 USD"
        montos = extraer_montos(texto)
        assert any("100" in str(monto) for monto in montos)
    
    def test_extraer_monto_con_euros(self):
        texto = "Ganaste 100 EUR"
        montos = extraer_montos(texto)
        assert any("100" in str(monto) for monto in montos)
    
    def test_extraer_monto_con_soles(self):
        texto = "Ganaste S/ 100"
        montos = extraer_montos(texto)
        assert any("100" in str(monto) for monto in montos)
    
    def test_sin_montos(self):
        texto = "Este texto no tiene montos"
        montos = extraer_montos(texto)
        assert montos == []
    
    def test_extraer_montos_none(self):
        """Test caso edge: texto None"""
        montos = extraer_montos(None)
        assert montos == []


class TestExtraerPalabrasClave:
    """Tests para la función extraer_palabras_clave"""
    
    def test_detectar_premio(self):
        texto = "Felicidades ganaste un premio"
        palabras = extraer_palabras_clave(texto)
        assert "premio" in palabras or "ganaste" in palabras
    
    def test_detectar_urgente(self):
        texto = "URGENTE: verifica tu cuenta"
        palabras = extraer_palabras_clave(texto)
        assert "urgente" in palabras or "verifica" in palabras
    
    def test_detectar_gratis(self):
        texto = "Obtén esto GRATIS ahora"
        palabras = extraer_palabras_clave(texto)
        assert "gratis" in palabras
    
    def test_detectar_banco(self):
        texto = "Tu banco requiere verificación"
        palabras = extraer_palabras_clave(texto)
        assert "banco" in palabras
    
    def test_detectar_click(self):
        texto = "Haz click aquí para ganar"
        palabras = extraer_palabras_clave(texto)
        assert "click" in palabras
    
    def test_sin_palabras_clave(self):
        texto = "Este es un mensaje normal"
        palabras = extraer_palabras_clave(texto)
        # Puede retornar lista vacía o con pocas palabras
        assert isinstance(palabras, list)
    
    def test_detectar_palabras_clave_none(self):
        """Test caso edge: texto None"""
        palabras = extraer_palabras_clave(None)
        assert palabras == []


class TestPreprocesarCompleto:
    """Tests para la función preprocesar_completo"""
    
    def test_pipeline_completo(self):
        texto = "¡FELICIDADES! Ganaste $1000 USD. Visita http://premio.com o contacta premio@fake.com"
        resultado = preprocesar_completo(texto)
        
        # Verificar estructura del diccionario
        assert "texto_limpio" in resultado
        assert "tokens" in resultado
        assert "urls" in resultado
        assert "emails" in resultado
        assert "numeros" in resultado
        assert "montos" in resultado
        assert "palabras_clave" in resultado
        
        # Verificar contenido
        assert isinstance(resultado["texto_limpio"], str)
        assert isinstance(resultado["tokens"], list)
        assert isinstance(resultado["urls"], list)
        assert isinstance(resultado["emails"], list)
        assert len(resultado["urls"]) > 0
        assert len(resultado["emails"]) > 0
    
    def test_mensaje_spam_real(self):
        # Ejemplo real de spam del dataset
        texto = "URGENT! You have won a 1 week FREE membership in our £100000 prize Jackpot!"
        resultado = preprocesar_completo(texto)
        
        assert len(resultado["palabras_clave"]) > 0
        assert len(resultado["tokens"]) > 0
    
    def test_mensaje_ham_real(self):
        # Ejemplo real de ham del dataset
        texto = "Ok lar... Joking wif u oni..."
        resultado = preprocesar_completo(texto)
        
        assert isinstance(resultado["texto_limpio"], str)
        assert len(resultado["tokens"]) > 0
    
    def test_texto_vacio(self):
        resultado = preprocesar_completo("")
        assert resultado["texto_limpio"] == ""
        assert resultado["tokens"] == []
        assert resultado["urls"] == []
        assert resultado["emails"] == []
    
    def test_preprocesar_none(self):
        """Test caso edge: texto None"""
        resultado = preprocesar_completo(None)
        assert resultado["texto_limpio"] == ""
        assert resultado["tokens"] == []
        assert resultado["urls"] == []
    
    def test_mensaje_spam_complejo(self):
        """Test con mensaje spam complejo del dataset"""
        texto = "FreeMsg: Txt: CALL to No: 86888 & claim your reward of 3 hours talk time to use from your phone now! ubscribe6GBP/ mnth inc 3hrs 16 stop?txtStop"
        resultado = preprocesar_completo(texto)
        
        assert len(resultado["palabras_clave"]) > 0
        assert len(resultado["numeros"]) > 0
        assert isinstance(resultado["texto_limpio"], str)


class TestRendimiento:
    """Tests de rendimiento del módulo PLN"""
    
    def test_rendimiento_100_mensajes(self):
        """Test: procesar 100 mensajes en menos de 1 segundo"""
        mensajes = [
            "URGENT! You have won a prize!",
            "Ok lar... Joking wif u oni...",
            "FreeMsg: Txt CALL to claim reward",
            "Hey, how are you doing today?",
            "Your bank account needs verification"
        ] * 20  # 100 mensajes
        
        inicio = time.time()
        for mensaje in mensajes:
            preprocesar_completo(mensaje)
        fin = time.time()
        
        tiempo_total = fin - inicio
        assert tiempo_total < 1.0, f"Procesamiento tomó {tiempo_total:.2f}s (esperado < 1s)"
    
    def test_rendimiento_texto_largo(self):
        """Test: procesar texto largo eficientemente"""
        texto_largo = " ".join([
            "URGENT! You have won a prize! Click here http://fake.com",
            "Contact us at spam@fake.com or call 123456789",
            "Claim your $1000 USD reward now! Limited time offer!"
        ] * 10)  # Texto muy largo
        
        inicio = time.time()
        resultado = preprocesar_completo(texto_largo)
        fin = time.time()
        
        tiempo_total = fin - inicio
        assert tiempo_total < 0.1, f"Procesamiento tomó {tiempo_total:.2f}s (esperado < 0.1s)"
        assert len(resultado["palabras_clave"]) > 0
        assert len(resultado["urls"]) > 0
