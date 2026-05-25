import sys
from pathlib import Path

# Make sure app package is importable
sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Reset password untuk akun guru
    guru = User.query.filter_by(username='guru1').first()
    if guru:
        new_password = 'Guru1234!'
        guru.set_password(new_password)
        db.session.commit()
        print(f"✅ Password untuk '{guru.username}' (role: {guru.role}) telah direset.")
        print(f"   Username: guru1")
        print(f"   Password: {new_password}")
    else:
        print("❌ Akun 'guru1' tidak ditemukan")
