import sys
from pathlib import Path

# Ensure the application package is importable (same pattern as other helper scripts)
sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.filter(User.role.in_(['admin','guru'])).order_by(User.id).all()
    print(f"Found {len(users)} admin/guru accounts:\n")
    for u in users:
        print(f"ID {u.id}: username={u.username}, name={u.name}, role={u.role}, created_at={u.created_at}")
