from datetime import date, datetime

from app import db


class UserGameHistory(db.Model):
    __tablename__ = 'user_game_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    game_id = db.Column(db.String(32), nullable=False, index=True)
    tanggal_main = db.Column(db.Date, nullable=False, default=date.today, index=True)
    status = db.Column(db.String(16), nullable=False, default='belum')
    answered_questions = db.Column(db.Integer, nullable=False, default=0)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    skor = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_id', 'tanggal_main', name='uq_user_game_history_user_game_day'),
    )
