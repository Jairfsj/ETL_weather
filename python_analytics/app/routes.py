from flask import Flask, jsonify, render_template
import pandas as pd
from .db import engine
from .alerts import send_alert

def create_routes(app: Flask):
    @app.route("/latest")
    def latest():
        try:
            df = pd.read_sql("""
                SELECT city, temperature, feels_like, humidity, pressure, wind_speed, wind_direction,
                       weather_main, weather_description, weather_icon,
                       to_timestamp(timestamp) as ts, created_at
                FROM weather_data
                ORDER BY timestamp DESC LIMIT 100;
            """, engine)
            return jsonify(df.to_dict(orient="records"))
        except Exception as e:
            send_alert(f"Error /latest endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/dashboard")
    def dashboard():
        try:
            df = pd.read_sql("""
                SELECT city, temperature, feels_like, humidity, pressure, wind_speed, wind_direction,
                       weather_main, weather_description, weather_icon,
                       to_timestamp(timestamp) as ts, created_at
                FROM weather_data
                ORDER BY timestamp DESC LIMIT 100;
            """, engine)

            # Current weather data (latest record)
            latest = df.iloc[0] if not df.empty else None

            # Chart data for temperature and humidity
            chart_data = {
                'temperature': df[['ts','temperature']].to_dict(orient='records'),
                'humidity': df[['ts','humidity']].to_dict(orient='records'),
                'feels_like': df[['ts','feels_like']].to_dict(orient='records') if 'feels_like' in df.columns else []
            }

            return render_template("dashboard.html",
                                 chart_data=chart_data,
                                 latest_weather=latest)
        except Exception as e:
            send_alert(f"Error /dashboard endpoint: {e}")
            return "Internal Server Error", 500
