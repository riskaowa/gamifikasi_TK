from datetime import datetime

from app import db


class AdventureQuestionMap(db.Model):
    __tablename__ = 'adventure_question_maps'

    id = db.Column(db.Integer, primary_key=True)
    game_key = db.Column(db.String(32), nullable=False, index=True)  # huruf | angka | warna
    level = db.Column(db.Integer, nullable=False, index=True)
    question_order = db.Column(db.Integer, nullable=False, index=True)  # 1..5 per level
    question_id = db.Column(db.Integer, db.ForeignKey('soal.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('game_key', 'level', 'question_order', name='uq_adventure_question_slot'),
    )
