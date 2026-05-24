from datetime import date, datetime

from app import db


class GamePlay(db.Model):
    __tablename__ = "game_plays"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    user_name = db.Column(db.String(100), nullable=False)
    game_name = db.Column(db.String(32), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    played_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    played_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "game_name", "played_date", name="uq_gameplay_user_game_date"),
    )
