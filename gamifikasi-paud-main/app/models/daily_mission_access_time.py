from app import db


class DailyMissionAccessTime(db.Model):
    __tablename__ = 'daily_mission_access_time'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        return f'<DailyMissionAccessTime {self.start_time}-{self.end_time}>'
