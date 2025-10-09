import os
import pytest
from ModeloML.infer_ml import load_pipeline, predict_label_score

@pytest.mark.skipif(not os.path.exists("backend/ModeloML/artifacts/sms_pipeline.joblib"),
                    reason="modelo no entrenado aún")
def test_predict_label_score():
    load_pipeline()
    lbl, sc = predict_label_score("Congratulations! You won a prize, click http://bit.ly/x")
    assert lbl in {"ham","smishing"}
    assert sc is None or (0.0 <= sc <= 1.0)
