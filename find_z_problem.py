import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

app = create_app()

with app.app_context():
    # Cari soal yang menampilkan Z
    huruf_soals = Soal.query.filter_by(kategori='huruf').all()
    
    print(f"\n{'='*80}")
    print(f"CARI SOAL YANG BERMASALAH DENGAN HURUF Z")
    print(f"{'='*80}\n")
    
    z_problems = []
    
    for soal in huruf_soals:
        # Cek apakah soal ini menampilkan Z atau menanyakan tentang Z
        pertanyaan = str(soal.pertanyaan).upper()
        jawaban_db = soal.jawaban_benar.upper()
        
        # Ambil pilihan yang sesuai jawaban database
        choices = {
            'A': soal.pilihan_a,
            'B': soal.pilihan_b,
            'C': soal.pilihan_c,
            'D': soal.pilihan_d,
        }
        correct_choice = choices.get(jawaban_db)
        
        # Gabungkan pilihan, handle None
        all_choices = (str(soal.pilihan_a or '') + str(soal.pilihan_b or '') + 
                      str(soal.pilihan_c or '') + str(soal.pilihan_d or '')).upper()
        
        # Jika soal tentang Z atau menampilkan Z tapi jawabannya bukan Z
        if 'Z' in pertanyaan or 'Z' in all_choices:
            print(f"ID {soal.id}: {soal.pertanyaan}")
            print(f"  Jawaban DB: {jawaban_db} ({correct_choice})")
            print(f"  A: {soal.pilihan_a}, B: {soal.pilihan_b}, C: {soal.pilihan_c}, D: {soal.pilihan_d}")
            
            # Jika pilihan A adalah "Z" tapi database mengatakan A bukan jawaban benar
            if soal.pilihan_a and 'Z' in str(soal.pilihan_a).upper():
                if jawaban_db != 'A':
                    print(f"  ⚠️  MASALAH: Pilihan A adalah 'Z' tapi jawaban DB adalah '{jawaban_db}'")
                    z_problems.append(soal)
            
            print()
    
    print(f"\n{'='*80}")
    print(f"TOTAL SOAL BERMASALAH: {len(z_problems)}")
    print(f"{'='*80}\n")
    
    if z_problems:
        print("Soal-soal yang akan dihapus:")
        for soal in z_problems:
            print(f"  - ID {soal.id}: {soal.pertanyaan[:50]}")
