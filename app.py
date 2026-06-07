from flask import Flask, render_template
from flask_cors import CORS
from routes.analytics import analytics_bp
from routes.predict import predict_bp
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
CORS(app)

app.register_blueprint(analytics_bp)
app.register_blueprint(predict_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)