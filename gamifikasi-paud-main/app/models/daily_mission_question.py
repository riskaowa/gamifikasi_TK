from datetime import date, datetime

from app import db


class DailyMissionQuestion(db.Model):
    __tablename__ = 'daily_mission_questions'

    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, nullable=False, default=date.today, index=True)
    question_order = db.Column(db.Integer, nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('soal.id', ondelete='SET NULL'), nullable=True, index=True)
    set_by_teacher = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('tanggal', 'question_order', name='uq_daily_mission_question_slot'),
    )
