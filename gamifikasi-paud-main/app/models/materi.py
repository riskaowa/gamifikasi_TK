from app import db
from datetime import datetime

class Materi(db.Model):
    __tablename__ = 'materi'

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(128), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    kategori = db.Column(db.String(64), nullable=True)
    link_youtube = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
