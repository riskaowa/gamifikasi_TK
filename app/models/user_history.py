from datetime import date

from app import db


class UserHistory(db.Model):
    __tablename__ = 'user_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('soal.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'question_id', 'date', name='uq_user_history_user_question_day'),
    )
