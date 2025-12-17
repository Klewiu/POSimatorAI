import pandas as pd
import joblib
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# =========================
# KONFIGURACJA
# =========================
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pos_estimations.csv"
MODEL_DIR = Path(__file__).resolve().parent

SEGMENT_THRESHOLD = 20  # granica dla modelu LARGE


# =========================
# 1. WCZYTANIE DANYCH
# =========================
df = pd.read_csv(
    DATA_PATH,
    sep=";",
    encoding="utf-8-sig",
    dtype=str
)

df = df.apply(
    lambda col: col.map(
        lambda x: x.strip().replace("\xa0", "") if isinstance(x, str) else x
    )
)

# =========================
# 2. KOLUMNY NUMERYCZNE
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
    "stopien_skomplikowania",
    "cena"
]

for col in numeric_features:
    df[col] = pd.to_numeric(
        df[col].str.replace(",", ".", regex=False),
        errors="coerce"
    )

df[numeric_features] = df[numeric_features].fillna(
    df[numeric_features].mean()
)

# =========================
# 3. KOLUMNY KATEGORYCZNE
# =========================
categorical_features = [
    "rodzaj_tworzywa",
    "rodzaj_displaya"
]

df[categorical_features] = df[categorical_features].fillna("Unknown")


# =========================
# 4. PODZIAŁ DANYCH
# =========================
df_large = df[df["naklad_szt"] > SEGMENT_THRESHOLD].copy()

print("Rekordy GLOBAL:", len(df))
print(f"Rekordy LARGE (>{SEGMENT_THRESHOLD}):", len(df_large))


# =========================
# 5. FUNKCJA TRENUJĄCA MODEL (log(y))
# =========================
def train_model(df_train, label):
    y = np.log(df_train["cena"])  # LOG TARGET
    X = df_train.drop(columns=["cena"])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features[:-1]),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=600,
        max_depth=10,
        min_samples_leaf=3,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)

    y_pred_log = pipeline.predict(X_test)
    y_pred = np.exp(y_pred_log)  # odwracamy log

    y_test_exp = np.exp(y_test)

    print(f"\n📊 WYNIKI – {label}")
    print("MAE test:", round(mean_absolute_error(y_test_exp, y_pred), 2))
    print("R2 test:", round(r2_score(y_test, y_pred_log), 3))

    mae_cv = -cross_val_score(
        pipeline,
        X,
        y,
        scoring="neg_mean_absolute_error",
        cv=5,
        n_jobs=-1
    )

    print("MAE CV mean (log target):", round(mae_cv.mean(), 2))
    print("MAE CV std  (log target):", round(mae_cv.std(), 2))

    return pipeline

# =========================
# 6. TRENING MODELI
# =========================
model_global = train_model(df, "GLOBAL")
model_large = train_model(df_large, "LARGE")


# =========================
# 7. ZAPIS MODELI
# =========================
joblib.dump(
    {
        "threshold": SEGMENT_THRESHOLD,
        "model_global": model_global,
        "model_large": model_large,
    },
    MODEL_DIR / "hybrid_log_models.pkl"
)

print("\n✅ Modele zapisane: hybrid_log_models.pkl")
