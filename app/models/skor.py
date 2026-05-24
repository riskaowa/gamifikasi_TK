from app import db
from datetime import datetime

class Skor(db.Model):
    __tablename__ = 'skor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    xp_didapat = db.Column(db.Integer, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
