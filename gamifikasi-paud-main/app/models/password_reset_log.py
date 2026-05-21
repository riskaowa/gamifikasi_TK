from datetime import datetime

from app import db


class PasswordResetLog(db.Model):
    __tablename__ = 'password_reset_logs'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reset_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
