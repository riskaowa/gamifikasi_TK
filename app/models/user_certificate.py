from datetime import date, datetime

from app import db


class UserCertificate(db.Model):
    __tablename__ = 'user_certificates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    issue_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    certificate_type = db.Column(db.String(32), nullable=False, default='Milestone Hari Ke-6')
    score_snapshot = db.Column(db.Integer, nullable=False, default=0)
    message = db.Column(db.String(255), nullable=False, default='Selamat atas pencapaian belajar Anda!')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'certificate_type', name='uq_user_certificate_type'),
    )
