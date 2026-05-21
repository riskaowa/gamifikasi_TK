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
    print(f"TEMUKAN SOAL HURUF B DAN Z YANG BERMASALAH")
    print(f"{'='*80}\n")
    print(f"Total soal huruf: {len(huruf_soals)}\n")
    
    problematic = []
    
    for soal in huruf_soals:
        correct_answer_text = get_correct_answer_text(soal)
        correct_answer_letter = extract_letter_from_choice(correct_answer_text)
        expected_answer_letter = soal.jawaban_benar.upper()
        
        is_consistent = correct_answer_letter == expected_answer_letter
        
        if not is_consistent:
            problematic.append(soal)
    
    print(f"Ditemukan {len(problematic)} soal yang tidak konsisten.\n")
    
    # Cari khusus untuk B dan Z
    b_z_problems = [s for s in problematic if 'B' in str(s.pertanyaan).upper() or 'Z' in str(s.pertanyaan).upper()]
    print(f"Soal yang mungkin terkait B atau Z: {len(b_z_problems)}\n")
    
    # Tampilkan semua soal bermasalah
    for i, soal in enumerate(problematic[:10], 1):
        correct_text = get_correct_answer_text(soal)
        correct_letter = extract_letter_from_choice(correct_text)
        print(f"{i}. ID {soal.id}: {soal.pertanyaan[:40]}")
        print(f"   DB jawaban: {soal.jawaban_benar}, Teks: {correct_text} ({correct_letter})")
        print(f"   A: {soal.pilihan_a}, B: {soal.pilihan_b}, C: {soal.pilihan_c}, D: {soal.pilihan_d}\n")
    
    if len(problematic) > 10:
        print(f"... dan {len(problematic) - 10} soal lainnya")
