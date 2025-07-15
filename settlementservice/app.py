from flask import Flask
from flask_jwt_extended import JWTManager
from settlementservice.config import Config
from settlementservice.extensions import db
from settlementservice.routes.settlement_routes import settlement_bp
from settlementservice.routes.debt_api import debt_api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(settlement_bp, url_prefix="/api/settlements")
    app.register_blueprint(debt_api, url_prefix="/api/debts")  # if applicable

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5003, debug=True)
