from authservice.extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
