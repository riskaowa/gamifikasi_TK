from app import db
from datetime import date

class ProgresHarian(db.Model):
    __tablename__ = 'progres_harian'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tanggal = db.Column(db.Date, nullable=False, default=date.today)
    status_selesai = db.Column(db.Boolean, nullable=False, default=False)
    target_xp = db.Column(db.Integer, nullable=False, default=50)  # Target XP per hari
    xp_earned = db.Column(db.Integer, nullable=False, default=0)  # XP yang didapat hari ini
    streak = db.Column(db.Integer, nullable=False, default=0)  # Streak hari berturut-turut
    bonus = db.Column(db.Integer, nullable=False, default=0)  # Bonus XP dari streak
    bintang = db.Column(db.Integer, nullable=False, default=0)  # Bintang untuk progres harian

    __table_args__ = (
        db.UniqueConstraint('user_id', 'tanggal', name='uq_progres_harian_user_date'),
    )
