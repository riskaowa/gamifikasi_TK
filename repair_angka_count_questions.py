import argparse

from app import create_app, db
from app.models.question import Soal


app = create_app()


def _get_answer_text(row):
    answer_letter = Soal.answer_key_to_letter(row.jawaban_benar)
    option_map = {
        'A': (row.pilihan_a or '').strip(),
        'B': (row.pilihan_b or '').strip(),
        'C': (row.pilihan_c or '').strip(),
        'D': (row.pilihan_d or '').strip(),
    }
    return option_map.get(answer_letter, '').strip()


def _resolve_count_label(row):
    current = (row.image_question or '').strip()
    if current.lower().startswith('count:'):
        parts = current.split(':', 2)
        if len(parts) >= 2 and parts[1].strip():
            return parts[1].strip()
    return 'benda'


def repair_legacy_angka_count_questions(dry_run=False, verbose=False):
    rows = Soal.query.filter_by(kategori='angka').filter(Soal.question_type == 'count_objects').order_by(Soal.id.asc()).all()

    inspected = len(rows)
    already_ok = 0
    repaired = 0
    skipped = []
    changed_ids = []

    for row in rows:
        answer_text = _get_answer_text(row)
        if not answer_text.isdigit():
            skipped.append((row.id, f'jawaban benar bukan angka: {answer_text or "kosong"}'))
            continue

        answer_value = int(answer_text)
        if answer_value < 1 or answer_value > 30:
            skipped.append((row.id, f'angka di luar rentang 1..30: {answer_value}'))
            continue

        desired_image = f'count:{_resolve_count_label(row)}:{answer_value}'
        current_image = (row.image_question or '').strip()
        if current_image == desired_image:
            already_ok += 1
            continue

        row.image_question = desired_image
        repaired += 1
        changed_ids.append(row.id)

        if verbose:
            print(f'[REPAIR] Soal #{row.id}: {current_image or "<kosong>"} -> {desired_image}')

    if repaired and not dry_run:
        db.session.commit()
    else:
        db.session.rollback()

    print('Repair soal angka count_objects selesai.')
    print(f'Dry run: {"ya" if dry_run else "tidak"}')
    print(f'Total diperiksa: {inspected}')
    print(f'Sudah benar: {already_ok}')
    print(f'Diperbaiki: {repaired}')
    print(f'Dilewati: {len(skipped)}')

    if changed_ids:
        joined_ids = ', '.join(str(question_id) for question_id in changed_ids)
        print(f'ID soal yang {"akan diperbaiki" if dry_run else "diperbaiki"}: {joined_ids}')

    if skipped:
        print('Soal yang dilewati:')
        for question_id, reason in skipped:
            print(f'- ID {question_id}: {reason}')


def main():
    parser = argparse.ArgumentParser(
        description='Perbaiki soal angka lama bertipe count_objects agar gambar jumlah benda sesuai dengan jawaban benar.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Cek soal yang akan diperbaiki tanpa menyimpan perubahan ke database.',
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Tampilkan detail setiap soal yang diperbaiki.',
    )
    args = parser.parse_args()

    with app.app_context():
        repair_legacy_angka_count_questions(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == '__main__':
    main()