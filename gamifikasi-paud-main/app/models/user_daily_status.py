from datetime import date, datetime

from app import db


class UserDailyStatus(db.Model):
    __tablename__ = 'user_daily_status'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    mission_completed = db.Column(db.Boolean, nullable=False, default=False)
    reminder_played = db.Column(db.Boolean, nullable=False, default=False)
    completion_audio_played = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_daily_status_user_date'),
    )
