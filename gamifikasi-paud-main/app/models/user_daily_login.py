from datetime import date, datetime

from app import db


class UserDailyLogin(db.Model):
    __tablename__ = 'user_daily_login'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    tanggal = db.Column(db.Date, nullable=False, default=date.today, index=True)
    bintang_didapat = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'tanggal', name='uq_user_daily_login_user_date'),
    )
