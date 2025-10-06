# Shield-SMS

Sistema de detección de smishing mediante Machine Learning y Procesamiento de Lenguaje Natural.

## Descripción

Shield-SMS es un proyecto desarrollado como parte del curso CIB02-O (Ingeniería de Software) que implementa un sistema de detección de mensajes SMS fraudulentos (smishing) utilizando técnicas de Machine Learning y Procesamiento de Lenguaje Natural.

## Estructura del Repositorio

```
Shield_SMS/
├── backend/
│   ├── api/              # API REST con FastAPI
│   ├── PLN/              # Módulos de Procesamiento de Lenguaje Natural
│   ├── ModeloML/         # Modelos de Machine Learning
│   ├── utils/            # Utilidades y funciones auxiliares
│   ├── data/             # Datasets y datos de entrenamiento
│   ├── requirements.txt  # Dependencias del proyecto
│   └── Dockerfile        # Configuración de Docker
├── tests/                # Tests unitarios y de integración
├── docs/                 # Documentación del proyecto
├── .github/workflows/    # Configuración de CI/CD
├── README.md
└── .gitignore
```

## Colaboradores

- Carlos Santana (carlos.santana.p@uni.pe)
- Antony Lipa (antony.lipa.b@uni.pe)
- Juan Gonzales (j.gonzales.avendano@uni.pe)
- Alexandro Achalma (alexandro.achalma.g@uni.pe)

## Tecnologías

- Python 3.9+
- FastAPI
- scikit-learn
- NLTK
- Pandas
- Pytest

## Licencia

Este proyecto es parte de un trabajo académico de la Universidad Nacional de Ingeniería (UNI).
