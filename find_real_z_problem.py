import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

app = create_app()

with app.app_context():
    huruf_soals = Soal.query.filter_by(kategori='huruf').all()
    
    print(f"\n{'='*80}")
    print(f"CARI SOAL DI MANA JAWABAN TIDAK SESUAI PILIHAN")
    print(f"{'='*80}\n")
    
    problematic = []
    
    for soal in huruf_soals:
        jawaban_db = soal.jawaban_benar.upper() if soal.jawaban_benar else ''
        
        choices = {
            'A': soal.pilihan_a or '',
            'B': soal.pilihan_b or '',
            'C': soal.pilihan_c or '',
            'D': soal.pilihan_d or '',
        }
        
        correct_choice_text = choices.get(jawaban_db, '')
        
        # Cek jika pilihan A ada isinya tapi database tidak mengatakan A
        if soal.pilihan_a and jawaban_db and jawaban_db != 'A':
            # Jika pilihan A adalah Z atau B atau huruf seharusnya menjadi jawaban
            pilihan_a_text = str(soal.pilihan_a).upper()
            
            # Jika pilihan_a berisi huruf, cek apakah seharusnya itu jawaban benar
            if pilihan_a_text and pilihan_a_text.isalpha():
                # Database mengatakan jawaban adalah pilihan lain, bukan A
                print(f"ID {soal.id}: {soal.pertanyaan}")
                print(f"  Pilihan A: {soal.pilihan_a} → Jawaban DB seharusnya A")
                print(f"  Tapi Jawaban DB sebenarnya: {jawaban_db} ({correct_choice_text})")
                print(f"  Pilihan: A={soal.pilihan_a}, B={soal.pilihan_b}, C={soal.pilihan_c}, D={soal.pilihan_d}")
                print()
                
                problematic.append(soal.id)
    
    print(f"\n{'='*80}")
    print(f"TOTAL SOAL PERLU DIHAPUS: {len(problematic)}")
    print(f"ID: {problematic}")
    print(f"{'='*80}\n")
