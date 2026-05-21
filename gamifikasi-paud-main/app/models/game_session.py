from datetime import date, datetime

from app import db


class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    game_name = db.Column(db.String(32), nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False)
    skor = db.Column(db.Integer, nullable=False, default=0)
    tanggal = db.Column(db.Date, nullable=False, default=date.today, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_name', 'tanggal', 'level', name='uq_game_session_user_game_day_level'),
    )