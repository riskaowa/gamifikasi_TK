from datetime import date, datetime

from app import db


class UserScore(db.Model):
    __tablename__ = 'user_scores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    game_id = db.Column(db.String(32), nullable=False, index=True)
    skor = db.Column(db.Integer, nullable=False, default=0)
    tanggal = db.Column(db.Date, nullable=False, default=date.today, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
