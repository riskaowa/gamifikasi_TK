"""
Script untuk mencari dan analisis soal yang bermasalah
"""

import sys
import os

# Adjust path to find app module
project_root = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main')
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import create_app, db
from app.models.question import Soal
import re


def extract_target_huruf_from_question(pertanyaan):
    """Extract huruf target dari pertanyaan"""
    # "Setelah huruf X adalah" -> X
    # "Sebelum huruf X adalah" -> X
    # "Huruf apa ini?" -> cek image
    match = re.search(r'huruf\s+([A-Za-z])\s+adalah', pertanyaan, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    # "Pasangan huruf besar dari (huruf lowercase)" 
    match = re.search(r'dari\s+([a-z])', pertanyaan, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    
    return None


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


app = create_app()

with app.app_context():
    # Cari soal yang terkait dengan huruf V, N, Y, R, G, E
    target_huruf = ['V', 'N', 'Y', 'R', 'G', 'E', 'F']
    
    print("PENCARIAN SOAL BERMASALAH")
    print("="*70)
    
    problematic = []
    
    all_rows = Soal.query.filter_by(kategori='huruf').order_by(Soal.id.asc()).all()
    
    for row in all_rows:
        pertanyaan = row.pertanyaan or ""
        answer_text = get_answer_text(row)
        
        # Extract target huruf dari pertanyaan
        target = extract_target_huruf_from_question(pertanyaan)
        
        # Check if this question is about one of our target letters
        is_relevant = False
        for huruf in target_huruf:
            if huruf in pertanyaan or (target and huruf in target):
                is_relevant = True
                break
        
        if is_relevant:
            # Untuk soal "Setelah/Sebelum huruf X adalah", validasi jawaban
            if "Setelah" in pertanyaan or "Sebelum" in pertanyaan:
                if target and len(answer_text) == 1 and answer_text.isalpha():
                    # Setelah X, jawaban harus huruf setelahnya
                    # Sebelum X, jawaban harus huruf sebelumnya
                    expected = None
                    if "Setelah" in pertanyaan:
                        expected = chr(ord(target) + 1)
                    elif "Sebelum" in pertanyaan:
                        expected = chr(ord(target) - 1)
                    
                    if expected and answer_text != expected:
                        problematic.append({
                            'id': row.id,
                            'pertanyaan': pertanyaan,
                            'target': target,
                            'expected': expected,
                            'actual': answer_text
                        })
                        print(f"\n⚠️  ID {row.id} - TIDAK SESUAI")
                        print(f"   Pertanyaan: {pertanyaan}")
                        print(f"   Target: {target}")
                        print(f"   Diharapkan: {expected}")
                        print(f"   Jawaban Sebenarnya: {answer_text}")
            
            # Untuk soal "Huruf apa ini?"
            elif "Huruf apa ini" in pertanyaan:
                # Jawaban harus berupa single huruf
                if len(answer_text) == 1 and answer_text.isalpha():
                    print(f"\nID {row.id} - CHECK")
                    print(f"   Pertanyaan: {pertanyaan}")
                    print(f"   Jawaban: {answer_text}")
                    print(f"   Opsi: A={row.pilihan_a}, B={row.pilihan_b}, C={row.pilihan_c}, D={row.pilihan_d}")
    
    print("\n" + "="*70)
    print(f"Total soal bermasalah ditemukan: {len(problematic)}")
    
    if problematic:
        print("\nDaftar ID untuk dihapus:")
        ids = [item['id'] for item in problematic]
        print(",".join(str(id) for id in ids))
