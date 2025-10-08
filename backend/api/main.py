# backend/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel

# ===== ML opcional (no falla si aún no existe) =====
try:
    from ml.infer_ml import predict_label_score, load_pipeline  # -> (label, score)
except Exception:  # noqa
    predict_label_score = None
    load_pipeline = None

# ===== Reglas opcionales (ajusta import a tu módulo real si lo tienes) =====
try:
    # Ejemplo: from backend.ModeloML.rules_model import classify_by_rules
    from ModeloML.rules_model import classify_by_rules  # -> (label, features)
except Exception:  # noqa
    classify_by_rules = None

app = FastAPI(title="Shield-SMS API")

class InText(BaseModel):
    text: str

@app.on_event("startup")
def on_startup():
    # Intentar cargar el modelo ML si existe (ruta por defecto o variable de entorno)
    if load_pipeline:
        try:
            load_pipeline()
        except Exception:
            pass

@app.get("/health")
def health():
    """Simple healthcheck + flag de si se cargó el modelo ML."""
    ml_ok = False
    if load_pipeline:
        import os
        ml_ok = os.path.exists(os.getenv("SMS_ML_PATH", "backend/ml/artifacts/sms_pipeline.joblib"))
    return {"status": "ok", "ml_loaded": ml_ok}

@app.post("/classify")
def classify(inp: InText):
    text = inp.text

    # 1) ML si está disponible
    if predict_label_score:
        try:
            out = predict_label_score(text)
            if out is not None:
                label, score = out
                return {
                    "label": label,
                    "score": float(score) if score is not None else None,
                    "source": "ml"
                }
        except Exception:
            # Si el modelo falla, continuamos al fallback
            pass

    # 2) Reglas si existen
    if classify_by_rules:
        try:
            label_rules, features = classify_by_rules(text)
            return {
                "label": label_rules,
                "score": None,
                "features_detected": features,
                "source": "rules"
            }
        except Exception:
            pass

    # 3) Fallback seguro
    return {"label": "ham", "score": None, "source": "fallback"}
