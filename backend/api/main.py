"""
API FastAPI para Shield-SMS
Implementación básica - Fase GREEN
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Crear instancia de FastAPI
app = FastAPI(
    title="Shield-SMS API",
    description="API para detección de smishing en mensajes SMS",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Endpoint de health check para verificar el estado de la API.
    
    Returns:
        Dict con status y nombre del servicio
    """
    return {
        "status": "ok",
        "service": "Shield-SMS API"
    }


@app.post("/classify")
async def classify_sms(request: Dict) -> Dict:
    """
    Endpoint para clasificar mensajes SMS como smishing o ham.
    
    Args:
        request: Diccionario con campo 'text' conteniendo el mensaje SMS
        
    Returns:
        Dict con label (smishing/ham), score (0.0-1.0) y texto original
        
    Raises:
        HTTPException: Si el campo 'text' no existe o está vacío
    """
    # Validar que existe el campo 'text'
    if "text" not in request:
        raise HTTPException(
            status_code=422,
            detail="Campo 'text' es requerido"
        )
    
    text = request["text"]
    
    # Validar que el texto no está vacío
    if not text or not text.strip():
        raise HTTPException(
            status_code=422,
            detail="El campo 'text' no puede estar vacío"
        )
    
    # Implementación dummy - retorna clasificación básica
    # En fases posteriores se integrará el modelo ML real
    return {
        "label": "ham",
        "score": 0.5,
        "text": text
    }
