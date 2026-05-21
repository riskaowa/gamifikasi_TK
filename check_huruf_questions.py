"""
Script untuk memeriksa soal huruf yang tidak sesuai dengan jawabannya
"""

import sys
import os

# Adjust path to find app module
project_root = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main')
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import create_app, db
from app.models.question import Soal


app = create_app()


def get_answer_text(row):
    """Mendapatkan teks jawaban berdasarkan jawaban_benar"""
    answer_letter = Soal.answer_key_to_letter(row.jawaban_benar)
    option_map = {
        'A': (row.pilihan_a or '').strip(),
        'B': (row.pilihan_b or '').strip(),
        'C': (row.pilihan_c or '').strip(),
        'D': (row.pilihan_d or '').strip(),
    }
    return option_map.get(answer_letter, '').strip()


def check_huruf_questions(verbose=True):
    """
    Memeriksa soal huruf apakah jawaban benar sesuai dengan pertanyaan
    """
    rows = Soal.query.filter_by(kategori='huruf').order_by(Soal.id.asc()).all()
    
    problematic = []
    valid = 0
    
    print(f"Memeriksa {len(rows)} soal huruf...\n")
    
    for row in rows:
        # Ambil pertanyaan - biasanya format "Pilih huruf yang sesuai gambar."
        # atau hanya menampilkan huruf target
        question_text = (row.pertanyaan or '').strip().lower()
        image_question = (row.image_question or '').strip().lower()
        
        # Ambil jawaban yang benar
        answer_text = get_answer_text(row)
        
        # Ekstrak huruf dari pertanyaan atau gambar
        # Cari single huruf dalam pertanyaan
        target_letter = None
        
        # Cek apakah ada huruf tunggal di pertanyaan
        for char in row.pertanyaan or '':
            if char.isalpha():
                target_letter = char.upper()
                break
        
        # Jika tidak ada, cek di pilihan-pilihan
        if not target_letter:
            for option in [row.pilihan_a, row.pilihan_b, row.pilihan_c, row.pilihan_d]:
                if option and len(option.strip()) == 1 and option.strip().isalpha():
                    # Ini mungkin hanya opsi, bukan pertanyaan
                    pass
        
        # Cek apakah jawaban adalah single huruf
        answer_is_single_letter = len(answer_text) == 1 and answer_text.isalpha()
        
        if verbose:
            print(f"ID: {row.id}")
            print(f"  Pertanyaan: {row.pertanyaan}")
            print(f"  Gambar: {row.image_question}")
            print(f"  Opsi A: {row.pilihan_a}")
            print(f"  Opsi B: {row.pilihan_b}")
            print(f"  Opsi C: {row.pilihan_c}")
            print(f"  Opsi D: {row.pilihan_d}")
            print(f"  Jawaban Benar: {Soal.answer_key_to_letter(row.jawaban_benar)} ({answer_text})")
        
        # Logic: untuk soal huruf yang menampilkan huruf di pertanyaan,
        # jawaban yang benar harus mencocokkan huruf tersebut
        # Cek dari format pertanyaan - biasanya ada huruf di gambar
        
        # Ekstrak dari image_question format "huruf:V" atau sejenisnya
        if ':' in image_question:
            parts = image_question.split(':')
            if len(parts) >= 2:
                target_from_image = parts[1].strip().upper()
                if target_from_image.isalpha() and len(target_from_image) == 1:
                    target_letter = target_from_image
        
        # Jika target_letter ditemukan, periksa apakah jawaban sesuai
        if target_letter and answer_is_single_letter:
            if target_letter.upper() != answer_text.upper():
                if verbose:
                    print(f"  ⚠️  TIDAK SESUAI: Huruf target '{target_letter}' tapi jawaban '{answer_text}'")
                problematic.append({
                    'id': row.id,
                    'target': target_letter,
                    'answer': answer_text,
                    'row': row
                })
            else:
                if verbose:
                    print(f"  ✓ Sesuai")
                valid += 1
        else:
            if verbose:
                print(f"  ? Tidak dapat diverifikasi")
        
        if verbose:
            print()
    
    print(f"\n{'='*60}")
    print(f"HASIL PEMERIKSAAN SOAL HURUF")
    print(f"{'='*60}")
    print(f"Total soal: {len(rows)}")
    print(f"Soal valid: {valid}")
    print(f"Soal bermasalah: {len(problematic)}")
    
    if problematic:
        print(f"\nSOAL YANG BERMASALAH:")
        for item in problematic:
            print(f"  ID {item['id']}: Target '{item['target']}' tapi jawaban '{item['answer']}'")
    
    return problematic


if __name__ == '__main__':
    with app.app_context():
        problematic = check_huruf_questions(verbose=True)
