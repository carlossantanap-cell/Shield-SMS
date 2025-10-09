
# Multi-stage Dockerfile para Shield-SMS Backend
# Optimizado para tamaño de imagen y seguridad

# Stage 1: Builder - Instalar dependencias
FROM python:3.10-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Descargar datos NLTK necesarios
RUN python -c "import nltk; nltk.download('stopwords', quiet=True, download_dir='/root/nltk_data')"

# Stage 2: Runtime - Imagen final optimizada
FROM python:3.10-slim

WORKDIR /app

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /root/nltk_data /home/appuser/nltk_data

# Configurar PATH y NLTK_DATA
ENV PATH=/home/appuser/.local/bin:$PATH
ENV NLTK_DATA=/home/appuser/nltk_data

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar a usuario no-root
USER appuser

# Exponer puerto 8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
