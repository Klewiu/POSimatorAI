import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

from pathlib import Path

# Ścieżka do danych
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pos_estimations.csv"

# 1. Wczytanie danych jako stringi (bez automatycznej konwersji)
df = pd.read_csv(DATA_PATH, sep=";", encoding="utf-8-sig", dtype=str)

# 2. Usunięcie zbędnych spacji i niewidocznych znaków
df = df.apply(lambda col: col.map(lambda x: x.strip().replace('\xa0', '') if isinstance(x, str) else x))

# 3. Kolumny numeryczne do konwersji
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
    "cena"
]

# Konwersja liczbowych kolumn na float (zamiana przecinka na kropkę)
for col in numeric_features:
    df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')

# Uzupełnienie braków w kolumnach numerycznych średnią kolumny
df[numeric_features] = df[numeric_features].fillna(df[numeric_features].mean())

# 4. Kolumny kategoryczne
categorical_features = ["rodzaj_tworzywa", "rodzaj_displaya", "stopien_skomplikowania"]

# Uzupełnienie braków w kategoriach
df[categorical_features] = df[categorical_features].fillna("Unknown")

# 5. Target i features
y = df["cena"]
X = df.drop(columns=["cena"])

print("Brakujące wartości w targetcie:", y.isna().sum())

# 6. Preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features[:-1]),  # wszystkie numeryczne oprócz targetu
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

# 7. Model
model = RandomForestRegressor(
    n_estimators=600,  # zwiększone dla lepszej stabilności
    max_depth=None,
    random_state=42,
    n_jobs=-1
)

# 8. Pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)

# 9. Split danych
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 10. Trening modelu
pipeline.fit(X_train, y_train)

# 11. Ewaluacja
y_pred = pipeline.predict(X_test)
print("MAE (średni błąd):", round(mean_absolute_error(y_test, y_pred), 2))
print("R2 (jakość modelu):", round(r2_score(y_test, y_pred), 3))

# 12. Zapis modelu
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"
joblib.dump(pipeline, MODEL_PATH)
print(f"✅ Model zapisany: {MODEL_PATH}")
