from flask import Flask, jsonify, render_template
import pandas as pd
from .db import engine
from .alerts import send_alert

def create_routes(app: Flask):
    @app.route("/latest")
    def latest():
        try:
            df = pd.read_sql("SELECT city, temperature, humidity,  wind_speed, to_timestamp(timestamp) as ts FROM weather_data ORDER BY timestamp DESC LIMIT 100;", engine)
            return jsonify(df.to_dict(orient="records"))
        except Exception as e:
            send_alert(f"Error /latest endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/dashboard")
    def dashboard():
        try:
            df = pd.read_sql("SELECT city, temperature,humidity, wind_speed, to_timestamp(timestamp) as ts FROM weather_data ORDER BY timestamp DESC LIMIT 100;", engine)
            chart_data = df[['ts','temperature']].to_dict(orient='records')
            return render_template("dashboard.html", chart_data=chart_data)
        except Exception as e:
            send_alert(f"Error /dashboard endpoint: {e}")
            return "Internal Server Error", 500
