import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

app = create_app()

with app.app_context():
    huruf_soals = Soal.query.filter_by(kategori='huruf').order_by(Soal.id).all()
    
    print(f"\n{'='*80}")
    print(f"SEMUA SOAL HURUF DI DATABASE SEKARANG")
    print(f"{'='*80}\n")
    print(f"Total: {len(huruf_soals)}\n")
    
    for soal in huruf_soals:
        print(f"{soal.id}. {soal.pertanyaan}")
        print(f"   Jawaban DB: {soal.jawaban_benar}")
        print(f"   A: {soal.pilihan_a}")
        print(f"   B: {soal.pilihan_b}")
        print(f"   C: {soal.pilihan_c}")
        print(f"   D: {soal.pilihan_d}")
        print()
