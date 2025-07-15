from flask import Flask
from splitservice.config import Config
from splitservice.extensions import db
from splitservice.routes.split_routes import split_bp
from splitservice.routes.split_api import split_api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(split_api)
    app.register_blueprint(split_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5002)
