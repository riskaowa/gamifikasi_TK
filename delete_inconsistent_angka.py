#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk memeriksa dan menghapus soal angka yang tidak sesuai game angka.
"""

import sys
from pathlib import Path

# Add the main app directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal


def delete_inconsistent_angka_soals(app):
    with app.app_context():
        bad_types = ['number_sequence', 'before_number']
        bad_soals = Soal.query.filter_by(kategori='angka').filter(Soal.question_type.in_(bad_types)).all()

        print('\n' + '=' * 80)
        print('PEMERIKSAAN SOAL ANGKA YANG TIDAK SESUAI')
        print('=' * 80 + '\n')
        print(f"Total soal angka: {Soal.query.filter_by(kategori='angka').count()}")
        print(f"Jumlah soal angka tidak sesuai (akan dihapus): {len(bad_soals)}\n")

        if not bad_soals:
            print('✅ Tidak ditemukan soal angka yang perlu dihapus.')
            return

        print('Contoh soal yang akan dihapus:')
        for soal in bad_soals[:10]:
            print(f"- ID {soal.id}: {soal.pertanyaan} | jawaban={soal.jawaban_benar} | options=[{soal.pilihan_a}, {soal.pilihan_b}, {soal.pilihan_c}, {soal.pilihan_d}]")
        if len(bad_soals) > 10:
            print(f"... dan {len(bad_soals) - 10} soal lainnya\n")

        confirm = input('Hapus semua soal angka tidak sesuai ini? Ketik YES untuk melanjutkan: ').strip()
        if confirm != 'YES':
            print('Dibatalkan.')
            return

        deleted_count = 0
        for soal in bad_soals:
            db.session.delete(soal)
            deleted_count += 1

        db.session.commit()
        print(f"\n✅ Selesai. Soal dihapus: {deleted_count}")


if __name__ == '__main__':
    app = create_app()
    delete_inconsistent_angka_soals(app)
