"""
Capa de inferencia para el modelo ML entrenado.
"""
import os
import joblib
from typing import Optional, Tuple

_PIPELINE = None
_PATH = os.getenv("SMS_ML_PATH", "backend/ModeloML/artifacts/sms_pipeline.joblib")

def load_pipeline(path: Optional[str] = None):
    global _PIPELINE
    p = path or _PATH
    if _PIPELINE is None and os.path.exists(p):
        _PIPELINE = joblib.load(p)
    return _PIPELINE

def predict_label_score(text: str) -> Optional[Tuple[str, float]]:
    """
    Devuelve (label, score_aprox). LinearSVC no da probas; usamos distancia
    al hiperplano como score relativo normalizado (0..1 aprox).
    """
    pipe = load_pipeline()
    if pipe is None:
        return None
    # predict
    label = pipe.predict([text])[0]
    # distancia como pseudo-score
    try:
        dec = pipe.decision_function([text])[0]
        # Convertimos a [0..1] aprox
        import math
        score = 1 / (1 + math.exp(-abs(float(dec))))
        return label, round(score, 4)
    except Exception:
        return label, None
