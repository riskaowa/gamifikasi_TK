from app import db

class Badge(db.Model):
    __tablename__ = 'badge'

    id = db.Column(db.Integer, primary_key=True)
    nama_badge = db.Column(db.String(128), nullable=False)
    deskripsi = db.Column(db.Text, nullable=True)
    level_minimum = db.Column(db.Integer, default=1)
