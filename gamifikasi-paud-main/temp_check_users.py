from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print('Existing users:', len(users))
    for u in users:
        print(u.id, u.username, u.role)

    required = [
        ('guru1', 'Guru Satu', 'guru', 'guru123'),
        ('murid1', 'Murid Satu', 'user', 'murid123'),
        ('ortu1', 'Orang Tua Satu', 'orangtua', 'ortu123')
    ]
    created = False
    for uname, name, role, pw in required:
        if not User.query.filter_by(username=uname).first():
            new_user = User(username=uname, name=name, role=role)
            new_user.set_password(pw)
            db.session.add(new_user)
            print('Created', uname, role)
            created = True
    if created:
        db.session.commit()
        print('Created sample users.')
    else:
        print('Sample users already exist.')
