"""
Script untuk analisis dan perbaikan soal huruf yang tidak sesuai dengan jawabannya
"""

import sys
import os

# Adjust path to find app module
project_root = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main')
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import create_app, db
from app.models.question import Soal


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


def extract_huruf_from_image(image_str):
    """Extract huruf dari image description"""
    if not image_str:
        return None
    
    # Format bisa berupa "huruf:A" atau SVG content dengan teks
    if ':' in image_str:
        parts = image_str.split(':')
        if len(parts) >= 2:
            target = parts[1].strip().upper()
            if len(target) == 1 and target.isalpha():
                return target
    
    # Coba extract dari SVG text element
    import re
    # Cari teks dalam <text> tag atau search untuk single uppercase letter
    # Contoh: >E< atau >G<
    matches = re.findall(r'[>%]([A-Za-z])[<;]', image_str)
    if matches:
        return matches[0].upper()
    
    return None


def analyze_problems(verbose=False):
    """Analisis dan collect soal-soal dengan jawaban yang tidak sesuai"""
    rows = Soal.query.filter_by(kategori='huruf').order_by(Soal.id.asc()).all()
    
    problematic = []
    
    for row in rows:
        answer_text = get_answer_text(row)
        
        # Ekstrak huruf dari image
        target_letter = extract_huruf_from_image(row.image_question)
        
        # Cek apakah jawaban adalah single huruf
        answer_is_single_letter = len(answer_text) == 1 and answer_text.isalpha()
        
        # Jika target_letter ditemukan dan jawaban adalah single huruf
        if target_letter and answer_is_single_letter:
            if target_letter.upper() != answer_text.upper():
                problematic.append({
                    'id': row.id,
                    'target': target_letter,
                    'answer': answer_text,
                    'pertanyaan': row.pertanyaan,
                })
    
    print(f"HASIL ANALISIS SOAL HURUF")
    print(f"{'='*70}")
    print(f"Total soal huruf: {len(rows)}")
    print(f"Soal dengan jawaban tidak sesuai: {len(problematic)}")
    
    if problematic:
        print(f"\nDaftar Soal Bermasalah (ID - Target: Jawaban Seharusnya -> Jawaban Salah):")
        print(f"{'-'*70}")
        for item in problematic:
            print(f"ID {item['id']:3d}: '{item['target']}' should be but answer is '{item['answer']}' - {item['pertanyaan'][:40]}")
        
        # Extract hanya ID untuk deletion
        ids_to_delete = [item['id'] for item in problematic]
        print(f"\n\nID Soal yang perlu dihapus:")
        print(",".join(str(id) for id in ids_to_delete))
    
    return problematic


def delete_problematic_questions(problematic_ids, dry_run=False):
    """Hapus soal-soal yang bermasalah"""
    if not problematic_ids:
        print("Tidak ada soal yang perlu dihapus")
        return
    
    print(f"\n{'='*70}")
    print(f"MODE: {'DRY RUN' if dry_run else 'AKTUAL'}")
    print(f"{'='*70}")
    
    deleted_count = 0
    for question_id in problematic_ids:
        row = Soal.query.get(question_id)
        if row:
            if not dry_run:
                db.session.delete(row)
            deleted_count += 1
    
    if not dry_run and deleted_count > 0:
        db.session.commit()
    elif dry_run:
        db.session.rollback()
    
    print(f"Soal yang {'akan dihapus' if dry_run else 'telah dihapus'}: {deleted_count}")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        problematic = analyze_problems(verbose=False)
        
        if problematic:
            import sys
            if len(sys.argv) > 1 and sys.argv[1] == 'delete':
                problematic_ids = [item['id'] for item in problematic]
                delete_problematic_questions(problematic_ids, dry_run=False)
                print("\n✓ Soal bermasalah telah dihapus dari database!")
            else:
                print("\n\nUntuk menghapus soal bermasalah, jalankan:")
                print("  python analyze_huruf_questions.py delete")
