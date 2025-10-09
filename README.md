# 🛡️ Shield-SMS - Detección de Smishing

[![CI/CD Pipeline](https://github.com/carlossantanap-cell/Shield-SMS/actions/workflows/ci.yml/badge.svg)](https://github.com/carlossantanap-cell/Shield-SMS/actions/workflows/ci.yml)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de detección de smishing (phishing por SMS) mediante Machine Learning y Procesamiento de Lenguaje Natural.

**Proyecto final del curso CIB02-O (Ingeniería de Software)**

## 📋 Descripción

Shield-SMS es un sistema inteligente que analiza mensajes SMS para detectar intentos de smishing utilizando:
- **Procesamiento de Lenguaje Natural (PLN)** para análisis de texto
- **Modelo de Machine Learning basado en reglas** para clasificación
- **API REST con FastAPI** para integración fácil
- **Validación de URLs** para detectar enlaces sospechosos

## ✨ Características

- ✅ Detección de smishing con 95.44% de accuracy
- ✅ Análisis de URLs sospechosas y acortadas
- ✅ Extracción de patrones: URLs, emails, números, montos
- ✅ API REST documentada con OpenAPI/Swagger
- ✅ 144 tests automatizados con TDD
- ✅ CI/CD con GitHub Actions
- ✅ Containerización con Docker

## 🚀 Inicio Rápido

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/carlossantanap-cell/Shield-SMS.git
cd Shield-SMS

# Instalar dependencias
pip install -r backend/requirements.txt

# Descargar datos NLTK
python -c "import nltk; nltk.download('stopwords')"

# Ejecutar tests
pytest tests/ -v

# Iniciar el servidor
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en `http://localhost:8000`

### Ejecutar con Docker

```bash
# Construir la imagen
docker build -t shield-sms-backend backend/

# Ejecutar el contenedor
docker run -p 8000:8000 shield-sms-backend
```

Accede a la documentación interactiva en `http://localhost:8000/docs`

## 📖 Uso de la API

### Health Check

```bash
curl http://localhost:8000/health
```

Respuesta:
```json
{
  "status": "ok",
  "service": "Shield-SMS API"
}
```

### Clasificar SMS

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENTE: Tu cuenta ha sido bloqueada. Haz clic aquí: http://bit.ly/fake123"}'
```

Respuesta:
```json
{
  "label": "smishing",
  "score": 0.85,
  "text": "URGENTE: Tu cuenta ha sido bloqueada. Haz clic aquí: http://bit.ly/fake123"
}
```

### Ejemplos de Uso

**Mensaje legítimo (ham):**
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Hola mamá, llegaré tarde a casa hoy. Te quiero."}'
```

**Mensaje de smishing:**
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Felicidades! Has ganado $5000. Reclama en: http://bit.ly/premio123"}'
```

## 🏗️ Arquitectura

```
Shield-SMS/
├── backend/
│   ├── api/              # API FastAPI
│   │   └── main.py       # Endpoints y modelos Pydantic
│   ├── PLN/              # Procesamiento de Lenguaje Natural
│   │   └── preprocessing.py
│   ├── ModeloML/         # Modelo de clasificación
│   │   └── rules_model.py
│   ├── utils/            # Utilidades
│   │   └── url_check.py  # Validación de URLs
│   ├── data/             # Dataset
│   │   └── dataset.csv   # SMSSpamCollection (5,572 mensajes)
│   └── requirements.txt
├── tests/                # Tests automatizados (144 tests)
│   ├── api_tests.py      # Tests de API (20 tests)
│   ├── pln_tests.py      # Tests de PLN (57 tests)
│   ├── model_tests.py    # Tests de Modelo (49 tests)
│   └── integracion_test.py  # Tests de integración (18 tests)
├── .github/
│   └── workflows/
│       └── ci.yml        # Pipeline CI/CD
└── docs/                 # Documentación
```

## 🧪 Tests

El proyecto cuenta con 144 tests automatizados siguiendo metodología TDD:

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests con coverage
pytest tests/ --cov=backend --cov-report=term-missing

# Ejecutar tests específicos
pytest tests/api_tests.py -v
pytest tests/pln_tests.py -v
pytest tests/model_tests.py -v
pytest tests/integracion_test.py -v
```

### Cobertura de Tests

- **API Tests (20)**: Endpoints, validaciones, casos edge
- **PLN Tests (57)**: Limpieza, tokenización, extracción de patrones
- **Modelo Tests (49)**: Clasificación, reglas, evaluación
- **Integración Tests (18)**: Flujo completo, rendimiento, concurrencia

## 📊 Rendimiento

- **Accuracy**: 95.44% en dataset SMSSpamCollection
- **Tiempo de respuesta**: < 100ms por mensaje
- **Procesamiento batch**: < 5s para 100 mensajes
- **Concurrencia**: Maneja múltiples requests simultáneos

## 🛠️ Tecnologías

- **Backend**: FastAPI 0.104.1, Python 3.10
- **ML/PLN**: scikit-learn, NLTK, pandas, numpy
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **CI/CD**: GitHub Actions
- **Containerización**: Docker
- **Documentación**: OpenAPI/Swagger

## 👥 Equipo de Desarrollo

| Colaborador | Email | GitHub | Contribución |
|-------------|-------|--------|--------------|
| **Carlos Santana** | carlos.santana.p@uni.pe | [@carlossantanap-cell](https://github.com/carlossantanap-cell) | API FastAPI + Endpoints (PR #1) |
| **Antony Lipa** | antony.lipa.b@uni.pe | [@akzykuner](https://github.com/akzykuner) | Módulo PLN + Preprocesamiento (PR #2) |
| **Juan Gonzales** | j.gonzales.avendano@uni.pe | [@juuuaaannn](https://github.com/juuuaaannn) | Modelo ML + Reglas (PR #3) |
| **Alexandro Achalma** | alexandro.achalma.g@uni.pe | [@alex03ac](https://github.com/alex03ac) | Integración + Utilidades (PR #4) |

## 📝 Metodología

El proyecto fue desarrollado siguiendo:
- ✅ **TDD (Test-Driven Development)**: Red → Green → Refactor
- ✅ **Git Flow**: Feature branches + Pull Requests
- ✅ **CI/CD**: Tests automáticos en cada push
- ✅ **Code Review**: Revisión de PRs antes de merge
- ✅ **Documentación**: Docstrings, type hints, README

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🔗 Enlaces

- [Documentación API](http://localhost:8000/docs)
- [GitHub Repository](https://github.com/carlossantanap-cell/Shield-SMS)
- [CI/CD Pipeline](https://github.com/carlossantanap-cell/Shield-SMS/actions)

---

**Universidad Nacional de Ingeniería (UNI)**  
**Curso**: CIB02-O - Ingeniería de Software  
**Fecha**: Octubre 2025
