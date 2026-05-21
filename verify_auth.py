from app import create_app, db
from app.models.user import User

app = create_app()

def test_auth():
    with app.app_context():
        # Test Registration
        test_user = User.query.filter_by(username='testuser').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
        
        new_user = User(username='testuser', name='Test User')
        new_user.set_password('password123')
        db.session.add(new_user)
        db.session.commit()
        
        user = User.query.filter_by(username='testuser').first()
        if user and user.check_password('password123'):
            print("Registration and Password Hashing: SUCCESS")
        else:
            print("Registration and Password Hashing: FAILED")
            
        # Test Admin Role
        admin = User.query.filter_by(username='admin').first()
        if admin and admin.role == 'admin':
            print("Admin Role Verification: SUCCESS")
        else:
            print("Admin Role Verification: FAILED")

if __name__ == "__main__":
    test_auth()
