from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from sqlalchemy import text
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
socketio = SocketIO(async_mode='threading')


def _ensure_default_audio_files():
    from app.models.audio_file import AudioFile

    defaults = {
        'misi_selesai': 'audio/selesaikanmisi.wav',
        'pengingat_misi': 'audio/pengingat_misi.wav',
        'login_reminder': 'audio/login_reminder.mp3',
        'mission_complete': 'audio/mission_complete.mp3',
        'home_background': 'audio/home.mp3',
        'selesai': 'audio/selesai.mp3'
    }

    changed = False
    for name, file_path in defaults.items():
        record = AudioFile.query.filter_by(name=name).first()
        if record:
            if record.file_path != file_path:
                record.file_path = file_path
                changed = True
            continue

        db.session.add(AudioFile(name=name, file_path=file_path))
        changed = True

    if changed:
        db.session.commit()


def _ensure_schema_compatibility():
    """Tambahkan kolom yang belum ada pada tabel lama agar model tetap kompatibel."""
    if db.engine.dialect.name != 'sqlite':
        return

    table_names = {
        row[0] for row in db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
    }

    if 'soal' in table_names:
        soal_columns = db.session.execute(text('PRAGMA table_info(soal)')).fetchall()
        soal_existing_cols = {row[1] for row in soal_columns}

        soal_pending_alters = []
        if 'pilihan_d' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN pilihan_d TEXT")
        if 'difficulty' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN difficulty VARCHAR(20) NOT NULL DEFAULT 'mudah'")
        if 'created_at' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN created_at DATETIME")
        if 'question_type' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN question_type VARCHAR(40)")
        if 'image_question' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN image_question TEXT")
        if 'image_option_a' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN image_option_a TEXT")
        if 'image_option_b' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN image_option_b TEXT")
        if 'image_option_c' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN image_option_c TEXT")
        if 'image_option_d' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN image_option_d TEXT")
        if 'use_in_daily_mission' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN use_in_daily_mission BOOLEAN NOT NULL DEFAULT 1")
        if 'use_in_adventure_map' not in soal_existing_cols:
            soal_pending_alters.append("ALTER TABLE soal ADD COLUMN use_in_adventure_map BOOLEAN NOT NULL DEFAULT 1")

        for stmt in soal_pending_alters:
            db.session.execute(text(stmt))

        if soal_pending_alters:
            db.session.execute(text("UPDATE soal SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))

    if 'users' in table_names:
        user_columns = db.session.execute(text('PRAGMA table_info(users)')).fetchall()
        user_existing_cols = {row[1] for row in user_columns}
        if 'created_at' not in user_existing_cols:
            db.session.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME"))
            db.session.execute(text("UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))

    if 'progres_harian' in table_names:
        progres_columns = db.session.execute(text('PRAGMA table_info(progres_harian)')).fetchall()
        progres_existing_cols = {row[1] for row in progres_columns}
        progres_pending_alters = []

        if 'bintang' not in progres_existing_cols:
            progres_pending_alters.append("ALTER TABLE progres_harian ADD COLUMN bintang INTEGER NOT NULL DEFAULT 0")

        for stmt in progres_pending_alters:
            db.session.execute(text(stmt))

        index_rows = db.session.execute(text("PRAGMA index_list('progres_harian')")).fetchall()
        index_names = {row[1] for row in index_rows}
        if 'uq_progres_harian_user_date' not in index_names:
            db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_progres_harian_user_date ON progres_harian(user_id, tanggal)"))

    db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)

    from app.models.user import User
    from app.models.audio_file import AudioFile
    from app.models.question import Soal
    from app.models.question_usage import QuestionUsage
    from app.models.adventure_question_map import AdventureQuestionMap
    from app.models.daily_mission_question import DailyMissionQuestion
    from app.models.materi import Materi
    from app.models.skor import Skor
    from app.models.progres_harian import ProgresHarian
    from app.models.badge import Badge
    from app.models.user_badge import UserBadge
    from app.models.game_play import GamePlay
    from app.models.game_session import GameSession
    from app.models.user_progress import UserProgress
    from app.models.user_daily_login import UserDailyLogin
    from app.models.user_daily_status import UserDailyStatus
    from app.models.user_game_history import UserGameHistory
    from app.models.password_reset_log import PasswordResetLog
    from app.models.user_history import UserHistory
    from app.models.user_scores import UserScore
    from app.models.user_certificate import UserCertificate
    from app.models.access_time import AccessTime
    from app.models.parent_student import ParentStudent
    from app.models.teacher_note import TeacherNote
    from app.models.daily_mission import DailyMissionRun
    from app.models.daily_mission_access_time import DailyMissionAccessTime

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()
        _ensure_schema_compatibility()
        _ensure_default_audio_files()

    return app
