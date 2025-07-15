from flask import Flask
from flask_cors import CORS
from invoiceservice.config import Config
from invoiceservice.extensions import db
from invoiceservice.routes.invoice_routes import invoice_bp

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    from models.invoice import Grocery

    db.create_all()

app.register_blueprint(invoice_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

# invoiceservice/extensions.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
