from flask import Flask
from  balanceservice.config import Config
from  balanceservice.extensions import db, jwt
from balanceservice.routes.balance_routes import balance_bp
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(balance_bp, url_prefix="/balance")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5004, debug=True)
