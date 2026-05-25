from app import create_app, db
from app.models.audio_file import AudioFile
from app.models.user import User
from app.models.question import Soal
from app.models.student_menu_access_time import StudentMenuAccessTime
from app.question_bank_generator import seed_question_bank

app = create_app()

def init_db():
    with app.app_context():
        try:
            db.drop_all()  # Drop all tables first
            db.create_all()
            print("Database initialized successfully!")
            
            # Create an admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(username='admin', name='Administrator', role='guru')
                admin.set_password('admin123') # Ganti segera setelah login
                db.session.add(admin)
                db.session.commit()
                print("Admin user created: admin / admin123")
            else:
                print("Admin user already exists.")

            inserted_questions = seed_question_bank(
                session=db.session,
                SoalModel=Soal,
                targets={
                    'angka': 140,
                    'huruf': 140,
                    'campuran': 140,
                },
            )
            print(f'Seed bank soal edukasi selesai. Soal baru ditambahkan: {inserted_questions}')

            default_audio_files = {
                'misi_selesai': 'audio/misi_selesai.wav',
                'pengingat_misi': 'audio/pengingat_misi.wav',
            }

            for name, file_path in default_audio_files.items():
                existing_audio = AudioFile.query.filter_by(name=name).first()
                if existing_audio:
                    if existing_audio.file_path != file_path:
                        existing_audio.file_path = file_path
                    continue
                db.session.add(AudioFile(name=name, file_path=file_path))

            db.session.commit()
            print('Data audio misi harian telah disiapkan.')

            # Seed badge templates
            from app.models.badge import Badge
            from app.models.user_badge import UserBadge

            if Badge.query.count() == 0:
                badges = [
                    Badge(nama_badge='Pemula', deskripsi='Mencapai Level 2', level_minimum=2),
                    Badge(nama_badge='Semangat', deskripsi='Mencapai Level 5', level_minimum=5),
                    Badge(nama_badge='Bintang', deskripsi='Mencapai Level 10', level_minimum=10),
                ]
                db.session.bulk_save_objects(badges)
                db.session.commit()
                print('Data badge telah ditambahkan.')
            else:
                print('Data badge sudah ada.')
        except Exception as e:
            print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_db()
