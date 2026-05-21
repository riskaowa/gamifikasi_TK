from datetime import datetime

from app import db


class UserProgress(db.Model):
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    game_id = db.Column(db.String(32), nullable=False, index=True)
    status = db.Column(db.String(16), nullable=False, default='belum')
    tanggal_update = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_id', name='uq_user_progress_user_game'),
    )