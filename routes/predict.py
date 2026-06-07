from flask import Blueprint, jsonify, request
from models.crime_model import predict_risk

predict_bp = Blueprint("predict", __name__)

@predict_bp.route("/api/predict", methods=["POST"])
def predict():
    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400
    result = predict_risk(
        crime_type=body.get("crime_type", "THEFT"),
        district=body.get("district", "1"),
        hour=int(body.get("hour", 12))
    )
    return jsonify(result)