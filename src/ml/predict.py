import joblib
import pandas as pd

MODEL_PATH = "ml/model.pkl"

model = joblib.load(MODEL_PATH)

def predict_price(data: dict) -> float:
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    return round(float(prediction), 2)