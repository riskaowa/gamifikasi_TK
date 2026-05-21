import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def extract_letter_from_choice(choice_text):
    """Extract single letter from choice text."""
    if not choice_text:
        return None
    text = str(choice_text).strip().upper()
    for char in text:
        if char.isalpha():
            return char
    return None

def get_correct_answer_text(question):
    """Get the text of the correct answer choice."""
    answer_map = {
        'A': question.pilihan_a,
        'B': question.pilihan_b,
        'C': question.pilihan_c,
        'D': question.pilihan_d,
    }
    answer_letter = question.jawaban_benar.upper()
    return answer_map.get(answer_letter, None)

app = create_app()

with app.app_context():
    huruf_soals = Soal.query.filter_by(kategori='huruf').all()
    
    print(f"\n{'='*80}")
    print(f"PEMERIKSAAN ULANG DAN PENGHAPUSAN SOAL HURUF YANG MASIH BERMASALAH")
    print(f"{'='*80}\n")
    print(f"Total soal huruf: {len(huruf_soals)}\n")
    
    # Periksa lagi konsistensi
    inconsistent_ids = []
    
    for soal in huruf_soals:
        correct_answer_text = get_correct_answer_text(soal)
        correct_answer_letter = extract_letter_from_choice(correct_answer_text)
        expected_answer_letter = soal.jawaban_benar.upper()
        
        # Check if answer matches the letter that should be correct
        if correct_answer_letter and correct_answer_letter != expected_answer_letter:
            inconsistent_ids.append(soal.id)
    
    if not inconsistent_ids:
        print("✅ Semua soal huruf KONSISTEN - tidak ada yang perlu dihapus!")
    else:
        print(f"⚠️  DITEMUKAN {len(inconsistent_ids)} SOAL MASIH BERMASALAH")
        print(f"Akan dihapus: {inconsistent_ids[:20]}{'...' if len(inconsistent_ids) > 20 else ''}\n")
        
        print(f"{'='*80}")
        print(f"MENGHAPUS {len(inconsistent_ids)} SOAL BERMASALAH...")
        print(f"{'='*80}\n")
        
        deleted_count = 0
        
        for soal_id in inconsistent_ids:
            soal = Soal.query.get(soal_id)
            if soal:
                try:
                    db.session.delete(soal)
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Error saat hapus soal ID {soal_id}: {e}")
        
        try:
            db.session.commit()
            print(f"\n{'='*80}")
            print(f"✅ SELESAI!")
            print(f"{'='*80}")
            print(f"✓ Soal dihapus: {deleted_count}")
            print(f"Sisa soal huruf: {len(huruf_soals) - deleted_count}")
            print(f"{'='*80}\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat commit: {e}")
