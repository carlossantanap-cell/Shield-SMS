"""
Entrena un modelo ML (TF-IDF + LinearSVC) sobre SMSSpamCollection o dataset.csv
y guarda vectorizador+modelo con joblib.

Uso:
  python -m ModeloML.train_ml --data backend/data/SMSSpamCollection.txt --out backend/ModeloML/artifacts
"""
import argparse
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def load_data(path: str) -> pd.DataFrame:
    # Adapta a tu dataset: SMSSpamCollection (tab-sep) o CSV con columnas ['label','text']
    if path.endswith(".txt"):
        df = pd.read_csv(path, sep="\t", header=None, names=["label","text"])
    else:
        df = pd.read_csv(path)
        assert {"label","text"} <= set(df.columns), "dataset debe tener columnas label y text"
    # Normaliza labels
    df["label"] = df["label"].map(lambda x: "smishing" if str(x).lower().startswith("spam") else "ham")
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="ruta dataset (SMSSpamCollection.txt o CSV)")
    ap.add_argument("--out", default="backend/ModeloML/artifacts", help="carpeta de salida")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    df = load_data(args.data)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"].values, df["label"].values, test_size=0.2, random_state=42, stratify=df["label"].values
    )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True, ngram_range=(1,2), min_df=2, max_df=0.98,
            strip_accents="unicode"
        )),
        ("clf", LinearSVC())
    ])

    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    print(classification_report(y_test, y_pred, digits=4))

    joblib.dump(pipe, os.path.join(args.out, "sms_pipeline.joblib"))
    print(f"Modelo guardado en {os.path.join(args.out, 'sms_pipeline.joblib')}")

if __name__ == "__main__":
    main()
