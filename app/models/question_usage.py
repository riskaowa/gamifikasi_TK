from datetime import datetime

from app import db


class QuestionUsage(db.Model):
    __tablename__ = 'question_usages'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('soal.id', ondelete='CASCADE'), nullable=False, index=True)
    context = db.Column(db.String(32), nullable=False, index=True)  # daily_mission | adventure_map
    game_key = db.Column(db.String(32), nullable=True, index=True)  # huruf | angka | warna (for adventure_map)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('question_id', 'context', 'game_key', name='uq_question_usage_scope'),
    )
