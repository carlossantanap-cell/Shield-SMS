"""
API FastAPI para Shield-SMS
Implementación con Pydantic y validaciones - Fase REFACTOR
Integración completa: API + PLN + Modelo ML
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Literal
import sys
from pathlib import Path

# Agregar el directorio backend al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos de PLN y Modelo
from PLN.preprocessing import preprocesar_completo
from ModeloML.rules_model import classify

# Modelos Pydantic para request/response

class SMSRequest(BaseModel):
    """
    Modelo para la solicitud de clasificación de SMS.
    
    Attributes:
        text: Texto del mensaje SMS a clasificar (1-1000 caracteres)
    
    Examples:
        >>> request = SMSRequest(text="Congratulations! You won a prize")
        >>> request.text
        'Congratulations! You won a prize'
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Texto del mensaje SMS a clasificar",
        examples=["Congratulations! You won a prize", "Hello, how are you?"]
    )
    
    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Valida que el texto no sea solo espacios en blanco."""
        if not v.strip():
            raise ValueError('El texto no puede estar vacío o contener solo espacios')
        return v


class SMSResponse(BaseModel):
    """
    Modelo para la respuesta de clasificación de SMS.
    
    Attributes:
        label: Clasificación del mensaje ('smishing' o 'ham')
        score: Puntuación de confianza de la clasificación (0.0-1.0)
        text: Texto original del mensaje clasificado
    
    Examples:
        >>> response = SMSResponse(label="ham", score=0.95, text="Hello")
        >>> response.label
        'ham'
    """
    label: Literal["smishing", "ham"] = Field(
        ...,
        description="Clasificación del mensaje: 'smishing' (malicioso) o 'ham' (legítimo)"
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Puntuación de confianza de la clasificación (0.0 = baja confianza, 1.0 = alta confianza)"
    )
    text: str = Field(
        ...,
        description="Texto original del mensaje clasificado"
    )


# Crear instancia de FastAPI con metadata completa
app = FastAPI(
    title="Shield-SMS API",
    description="""
    API REST para detección de smishing (phishing por SMS) en mensajes de texto.
    
    ## Características
    
    * **Clasificación de SMS**: Determina si un mensaje es smishing o ham (legítimo)
    * **Puntuación de confianza**: Proporciona un score de 0.0 a 1.0
    * **Validación robusta**: Valida longitud y contenido de los mensajes
    * **Health check**: Endpoint para monitoreo del estado del servicio
    
    ## Uso
    
    Envía un mensaje SMS al endpoint `/classify` y recibe una clasificación instantánea.
    """,
    version="0.1.0",
    contact={
        "name": "Equipo Shield-SMS",
        "email": "carlos.santana.p@uni.pe"
    },
    license_info={
        "name": "MIT"
    }
)

# Configurar CORS para permitir requests desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check del servicio",
    response_description="Estado del servicio"
)
async def health_check() -> dict[str, str]:
    """
    Endpoint de health check para verificar el estado de la API.
    
    Este endpoint se utiliza para monitoreo y verificación de que el servicio
    está funcionando correctamente.
    
    Returns:
        Diccionario con el estado del servicio y su nombre
        
    Example:
        ```python
        response = requests.get("http://localhost:8000/health")
        # {"status": "ok", "service": "Shield-SMS API"}
        ```
    """
    return {
        "status": "ok",
        "service": "Shield-SMS API"
    }


@app.post(
    "/classify",
    response_model=SMSResponse,
    tags=["Classification"],
    summary="Clasificar mensaje SMS",
    response_description="Resultado de la clasificación"
)
async def classify_sms(request: SMSRequest) -> SMSResponse:
    """
    Endpoint para clasificar mensajes SMS como smishing o ham.
    
    Analiza el contenido de un mensaje SMS y determina si es un intento de
    smishing (phishing por SMS) o un mensaje legítimo (ham).
    
    Args:
        request: Objeto SMSRequest con el texto del mensaje a clasificar
        
    Returns:
        Objeto SMSResponse con la clasificación, score de confianza y texto original
        
    Raises:
        HTTPException 422: Si el texto está vacío, es muy largo (>1000 caracteres)
                          o contiene solo espacios en blanco
        HTTPException 500: Si ocurre un error interno durante la clasificación
        
    Examples:
        ```python
        # Ejemplo de request
        request_data = {"text": "Congratulations! You won $1000. Click here to claim."}
        response = requests.post("http://localhost:8000/classify", json=request_data)
        
        # Ejemplo de response
        # {
        #   "label": "smishing",
        #   "score": 0.92,
        #   "text": "Congratulations! You won $1000. Click here to claim."
        # }
        ```
    """
    try:
        # Integración completa: PLN + Modelo ML
        # 1. Preprocesar texto con PLN (opcional, el modelo ya lo hace internamente)
        texto_procesado = preprocesar_completo(request.text)
        
        # 2. Clasificar con el modelo ML basado en reglas
        resultado = classify(request.text)
        
        # 3. Retornar respuesta estructurada
        return SMSResponse(
            label=resultado["label"],
            score=resultado["score"],
            text=request.text
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al clasificar el mensaje: {str(e)}"
        )
