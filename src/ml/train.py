import pandas as pd
import joblib
import numpy as np
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split, cross_val_score, RepeatedKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# =========================
# CONFIG
# =========================
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pos_estimations.csv"
MODEL_DIR = Path(__file__).resolve().parent

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(
    DATA_PATH,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

# cleanup string spaces
df = df.apply(
    lambda col: col.map(
        lambda x: x.strip().replace("\xa0", "") if isinstance(x, str) else x
    )
)

# =========================
# FEATURES
# =========================
numeric_features = [
    "naklad_szt",
    "objetosc_m3",
    "konstrukcja_kg",
    "sklejka_m3",
    "drewno_m3",
    "plyta_m2",
    "druk_m2",
    "led_mb",
    "tworzywa_m2",
    "koszty_pozostale",
    "stopien_skomplikowania"
]

target = "cena"

categorical_features = [
    "rodzaj_tworzywa",
    "rodzaj_displaya"
]

# =========================
# CONVERT TYPES
# =========================
for col in numeric_features + [target]:
    df[col] = pd.to_numeric(
        df[col].str.replace(",", ".", regex=False),
        errors="coerce"
    )

# =========================
# MISSING VALUES (NO LEAKAGE)
# =========================
for col in numeric_features:
    df[col] = df[col].fillna(df[col].median())

df[target] = df[target].fillna(df[target].median())

df[categorical_features] = df[categorical_features].fillna("Unknown")

# =========================
# TRAIN FUNCTION
# =========================
def train_model(df_train):

    y = df_train[target]
    X = df_train.drop(columns=[target])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    rf_params = dict(
        n_estimators=700,
        max_depth=12,
        min_samples_leaf=2,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    model = RandomForestRegressor(**rf_params)

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    # =========================
    # TRAIN / TEST SPLIT
    # =========================
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    mae_test = mean_absolute_error(y_test, y_pred)
    r2_test = r2_score(y_test, y_pred)

    # =========================
    # CROSS VALIDATION
    # =========================
    cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=42)

    mae_cv = -cross_val_score(
        pipeline,
        X,
        y,
        scoring="neg_mean_absolute_error",
        cv=cv,
        n_jobs=-1
    )

    # =========================
    # OUTPUT
    # =========================
    model_name = f"MODEL_GLOBAL_{datetime.now().strftime('%Y%m%d')}"

    print(f"\n📊 WYNIKI – {model_name}")
    print("MAE test:", round(mae_test, 2))
    print("R2 test:", round(r2_test, 3))
    print("MAE CV mean:", round(mae_cv.mean(), 2))
    print("MAE CV std:", round(mae_cv.std(), 2))

    return {
        "name": model_name,
        "pipeline": pipeline,
        "mae": round(mae_test, 2),
        "r2": round(r2_test, 3),
        "model_type": "RandomForestRegressor",
        "model_params": rf_params
    }

# =========================
# TRAIN
# =========================
model_global = train_model(df)

# =========================
# SAVE
# =========================
joblib.dump(
    {"model_global": model_global},
    MODEL_DIR / "model_global.pkl"
)

print("\n✅ Model zapisany: model_global.pkl")