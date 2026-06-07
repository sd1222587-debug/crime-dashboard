import pickle
import os
import mysql.connector
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

load_dotenv()
MODEL_PATH = "models/crime_model.pkl"

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

def assign_risk(row):
    high_crimes = ["ASSAULT","ROBBERY","HOMICIDE","BATTERY","KIDNAPPING"]
    if row["crime_type"] in high_crimes and row["hour"] in range(20,24):
        return "High"
    elif row["crime_type"] in high_crimes:
        return "Medium"
    else:
        return "Low"

def train_model():
    print("Loading data from database...")
    conn = get_conn()
    df = pd.read_sql("SELECT crime_type, district, hour FROM crimes LIMIT 50000", conn)
    conn.close()

    df = df.dropna()
    df["risk_level"] = df.apply(assign_risk, axis=1)

    le_type = LabelEncoder()
    le_dist = LabelEncoder()
    df["type_enc"] = le_type.fit_transform(df["crime_type"])
    df["dist_enc"] = le_dist.fit_transform(df["district"].astype(str))

    X = df[["type_enc","dist_enc","hour"]]
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
        d = le_dist.transform([str(float(district))])[0]
    except ValueError:
        return {"risk_level": "Unknown", "confidence": 0.0}
    proba = model.predict_proba([[t, d, hour]])[0]
    label = model.classes_[proba.argmax()]
    return {
        "risk_level": label,
        "confidence": round(float(proba.max()) * 100, 1)
    }