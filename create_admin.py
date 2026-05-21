import sys
from pathlib import Path

# Make sure app package is importable
sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.user import User

USERNAME = 'ADMIN'
DISPLAY_NAME = 'Administrator (ADMIN)'
PASSWORD = 'Admin1234!'
ROLE = 'admin'

app = create_app()

with app.app_context():
    existing = User.query.filter_by(username=USERNAME).first()
    if existing:
        print(f"User '{USERNAME}' already exists (id={existing.id}). Updating role and password.")
        existing.role = ROLE
        existing.set_password(PASSWORD)
        db.session.commit()
        print(f"Updated user '{USERNAME}' with role='{ROLE}'. New password is: {PASSWORD}")
    else:
        new_user = User(username=USERNAME, name=DISPLAY_NAME, role=ROLE)
        new_user.set_password(PASSWORD)
        db.session.add(new_user)
        db.session.commit()
        print(f"Created user '{USERNAME}' (id={new_user.id}) with role='{ROLE}'. Password: {PASSWORD}")
