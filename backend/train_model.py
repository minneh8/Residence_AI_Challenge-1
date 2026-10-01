from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from app.services.feature_extractor import FEATURE_NAMES

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'dataset_duat_final.csv'
OUTPUT = Path(__file__).resolve().parent / 'app' / 'models' / 'duat_model.joblib'
LABEL_CANDIDATES = ['rotulo', 'label', 'classificacao', 'target', 'y']


def main():
    df = pd.read_csv(DATASET)
    label = next((column for column in LABEL_CANDIDATES if column in df.columns), None)
    if label is None:
        raise ValueError(f'Nenhuma coluna de rótulo encontrada. Colunas: {list(df.columns)}')
    missing = [column for column in FEATURE_NAMES if column not in df.columns]
    if missing:
        raise ValueError(f'Features ausentes no dataset: {missing}')

    X = df[FEATURE_NAMES]
    y = df[label]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('classifier', RandomForestClassifier(
            n_estimators=300, random_state=42, class_weight='balanced', n_jobs=-1
        )),
    ])
    model.fit(X_train, y_train)
    print(classification_report(y_test, model.predict(X_test)))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUTPUT)
    print(f'Modelo salvo em {OUTPUT}')


if __name__ == '__main__':
    main()
