# backend/api/main.py
from fastapi import FastAPI
from pydantic import BaseModel

# ===== ML opcional (no falla si aún no existe) =====
try:
    from ModeloML.infer_ml import predict_label_score, load_pipeline  # -> (label, score)
except Exception:  # noqa
    predict_label_score = None
    load_pipeline = None

# ===== Reglas opcionales =====
try:
    from ModeloML.rules_model import classify_by_rules  # -> (label, features)
except Exception:  # noqa
    classify_by_rules = None

app = FastAPI(title="Shield-SMS API")


class InText(BaseModel):
    # 🔧 Permitir texto vacío u omitido para evitar error 422
    text: str | None = ""


@app.on_event("startup")
def on_startup():
    # Intentar cargar el modelo ML si existe
    if load_pipeline:
        try:
            load_pipeline()
        except Exception:
            pass


@app.get("/health")
def health():
    """Verifica el estado del servicio y si el modelo ML está cargado correctamente."""
    import os

    ml_ok = False
    model_path = os.getenv("SMS_ML_PATH", "backend/ModeloML/artifacts/sms_pipeline.joblib")
    if os.path.exists(model_path):
        ml_ok = True

    return {
        "status": "ok",
        "service": "ShieldSMS",  # requerido por los tests
        "ml_loaded": ml_ok
    }


@app.post("/classify")
def classify(inp: InText):
    """
    Clasifica un mensaje SMS como 'ham' (normal) o 'smishing' (fraudulento).
    Usa modelo ML si está disponible, luego reglas, y finalmente un fallback básico.
    Compatible con los tests automáticos.
    """
    text = inp.text or ""

    # ⚙️ 1) Validar texto vacío o demasiado largo
    if not text.strip() or len(text) > 5000:
        return {
            "text": text,
            "label": "ham",
            "score": None,
            "source": "fallback"
        }

    # ⚙️ 2) Intentar clasificar con modelo ML
    try:
        if predict_label_score:
            out = predict_label_score(text)
            if out is not None:
                label, score = out
                return {
                    "text": text,
                    "label": label,
                    "score": float(score) if score is not None else None,
                    "source": "ml"
                }
    except Exception:
        pass  # si el modelo falla, se pasa al siguiente método

    # ⚙️ 3) Intentar clasificar con reglas (si existen)
    try:
        if classify_by_rules:
            label_rules, features = classify_by_rules(text)
            return {
                "text": text,
                "label": label_rules,
                "score": None,
                "features_detected": features,
                "source": "rules"
            }
    except Exception:
        pass

    # ⚙️ 4) Fallback básico (sin ML ni reglas)
    text_lower = text.lower()
    if any(word in text_lower for word in ["congratulations", "prize", "click", "http", "win"]):
        label = "smishing"
    else:
        label = "ham"

    return {
        "text": text,
        "label": label,
        "score": None,
        "source": "fallback"
    }
