from invoiceservice.extensions import db

class Grocery(db.Model):
    __tablename__ = 'groceries'

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    item = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    totalSum = db.Column(db.Float)
    billId = db.Column(db.String(50))
    shopName = db.Column(db.String(100))
    address = db.Column(db.String(255))
    date = db.Column(db.Date)

    def __repr__(self):
        return f"<Grocery {self.item} - {self.price}>"
