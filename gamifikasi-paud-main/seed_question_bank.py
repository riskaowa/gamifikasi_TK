from app import create_app, db
from app.models.question import Soal
from app.question_bank_generator import seed_question_bank


app = create_app()


def run_seed():
    with app.app_context():
        inserted = seed_question_bank(
            session=db.session,
            SoalModel=Soal,
            targets={
                'angka': 140,
                'huruf': 140,
                'campuran': 140,
            },
        )
        total = Soal.query.count()
        angka = Soal.query.filter_by(kategori='angka').count()
        huruf = Soal.query.filter_by(kategori='huruf').count()
        campuran = Soal.query.filter_by(kategori='campuran').count()

        print('Seed bank soal selesai.')
        print(f'Soal baru ditambahkan: {inserted}')
        print(f'Total soal saat ini: {total}')
        print(f'Detail kategori -> angka: {angka}, huruf: {huruf}, campuran: {campuran}')


if __name__ == '__main__':
    run_seed()
