from flask import Blueprint, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
analytics_bp = Blueprint("analytics", __name__)

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME")
    )

@analytics_bp.route("/api/summary")
def summary():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM crimes")
    total = cur.fetchone()["total"]

    cur.execute("SELECT crime_type, COUNT(*) AS count FROM crimes GROUP BY crime_type ORDER BY count DESC LIMIT 10")
    by_type = cur.fetchall()

    cur.execute("SELECT district, COUNT(*) AS count FROM crimes GROUP BY district ORDER BY count DESC")
    by_district = cur.fetchall()

    cur.execute("SELECT MONTH(date) AS month, COUNT(*) AS count FROM crimes GROUP BY MONTH(date) ORDER BY month")
    by_month = cur.fetchall()

    cur.execute("SELECT hour, COUNT(*) AS count FROM crimes GROUP BY hour ORDER BY hour")
    by_hour = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "total": total,
        "by_type": by_type,
        "by_district": by_district,
        "by_month": by_month,
        "by_hour": by_hour
    })

@analytics_bp.route("/api/hotspots")
def hotspots():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT district, COUNT(*) AS incidents,
               MAX(crime_type) AS top_crime
        FROM crimes
        GROUP BY district
        ORDER BY incidents DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(rows)