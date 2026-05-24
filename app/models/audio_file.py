from datetime import datetime

from app import db


class AudioFile(db.Model):
    __tablename__ = 'audio_files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True, index=True)
    file_path = db.Column(db.Text, nullable=True)
    file_blob = db.Column(db.LargeBinary, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
