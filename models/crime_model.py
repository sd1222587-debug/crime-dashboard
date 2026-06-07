import pandas as pd
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

MODEL_PATH = "models/crime_model.pkl"

def assign_risk(row):
    high_crimes = ["ASSAULT", "ROBBERY", "HOMICIDE", "BATTERY", "KIDNAPPING"]
    if row["crime_type"] in high_crimes and row["hour"] in range(20, 24):
        return "High"
    elif row["crime_type"] in high_crimes:
        return "Medium"
    else:
        return "Low"

def train_model():
    print("Loading data...")
    df = pd.read_csv("data/crime_data.csv", low_memory=False)
    df = df.rename(columns={"Primary Type": "crime_type", "District": "district"})
    df["date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    df["hour"] = df["date"].dt.hour
    df = df[["crime_type", "district", "hour"]].dropna()
    df = df.head(50000)
    df["risk_level"] = df.apply(assign_risk, axis=1)

    le_type = LabelEncoder()
    le_dist = LabelEncoder()
    df["type_enc"] = le_type.fit_transform(df["crime_type"])
    df["dist_enc"] = le_dist.fit_transform(df["district"].astype(str))

    X = df[["type_enc", "dist_enc", "hour"]]
    y = df["risk_level"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "le_type": le_type, "le_dist": le_dist}, f)
    print("Model saved!")

def predict_risk(crime_type: str, district: str, hour: int) -> dict:
    if not os.path.exists(MODEL_PATH):
        train_model()
    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    model = bundle["model"]
    le_type = bundle["le_type"]
    le_dist = bundle["le_dist"]
    try:
        t = le_type.transform([crime_type.upper()])[0]
        d = le_dist.transform([str(district)])[0]
    except ValueError:
        return {"risk_level": "Unknown", "confidence": 0.0}
    proba = model.predict_proba([[t, d, hour]])[0]
    label = model.classes_[proba.argmax()]
    return {
        "risk_level": label,
        "confidence": round(float(proba.max()) * 100, 1)
    }