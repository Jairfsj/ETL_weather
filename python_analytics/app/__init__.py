from flask import Flask 
from .routes import create_routes

def create_app():
    app = Flask(__name__, tempate_folder="templates")
    create_routes(app)
    return app

if  __name__ == "__main__":
    import os 
    app = create_app()
    app.run(host=Os.getenv("FLASK_HOST","0.0.0.0"), port=int(os.getenv("FLASK_HOST",5000)))
