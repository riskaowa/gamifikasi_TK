from datetime import date, datetime

from app import db


class DailyMissionRun(db.Model):
    __tablename__ = 'daily_mission_runs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tanggal = db.Column(db.Date, nullable=False, default=date.today, index=True)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    answered_questions = db.Column(db.Integer, nullable=False, default=0)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    total_attempts = db.Column(db.Integer, nullable=False, default=0)
    timeout_reached = db.Column(db.Boolean, nullable=False, default=False)
    status_selesai = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'tanggal', name='uq_daily_mission_user_day'),
    )
