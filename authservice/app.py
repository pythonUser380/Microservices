import time
from flask import Flask
from flask_cors import CORS
from authservice.config import Config
from authservice.extensions import db, jwt, bcrypt
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)



with app.app_context():
    retries = 5
    while retries > 0:
        try:
            from authservice.models.user import User
            db.create_all()
            break
        except OperationalError:
            retries -= 1
            print("Database not ready, retrying in 5 seconds...")
            time.sleep(5)

from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
