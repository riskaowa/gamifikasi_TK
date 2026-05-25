#!/usr/bin/env python3
"""
Script untuk memperbaiki soal huruf:
1. Menambahkan opsi D yang hilang
2. Mengacak jawaban benar (tidak semua A)
3. Mengacak urutan pilihan
"""

import sys
from pathlib import Path
import random
from string import ascii_uppercase

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def get_unused_letters(a, b, c, used_count=3):
    """Dapatkan huruf yang belum digunakan."""
    used = set()
    
    # Extract first letter dari setiap pilihan
    for pilihan in [a, b, c]:
        if pilihan:
            first_char = str(pilihan).strip()[0].upper()
            if first_char.isalpha():
                used.add(first_char)
    
    # Cari huruf yang belum digunakan
    available = []
    for letter in ascii_uppercase:
        if letter not in used:
            available.append(letter)
    
    return available[:10]  # Return 10 huruf alternatif

def fix_huruf_questions():
    """Perbaiki soal huruf."""
    
    app = create_app()
    
    with app.app_context():
        huruf_questions = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"MEMPERBAIKI SOAL HURUF")
        print(f"{'='*80}\n")
        
        fixed_count = 0
        
        for q in huruf_questions:
            # Step 1: Jika D kosong, tambahkan opsi yang bermakna
            if not q.pilihan_d:
                # Dapatkan huruf yang belum digunakan
                available = get_unused_letters(q.pilihan_a, q.pilihan_b, q.pilihan_c)
                if available:
                    # Pilih huruf random dari yang tersedia
                    random_letter = random.choice(available)
                    q.pilihan_d = random_letter
            
            # Step 2: Acak urutan pilihan
            pilihan_map = {
                'A': q.pilihan_a,
                'B': q.pilihan_b,
                'C': q.pilihan_c,
                'D': q.pilihan_d,
            }
            
            # Buat list pilihan dan shuffle
            pilihan_list = list(pilihan_map.items())
            random.shuffle(pilihan_list)
            
            # Cari posisi jawaban lama
            old_answer = q.jawaban_benar.upper()
            correct_answer_text = pilihan_map[old_answer]
            
            # Perbarui pilihan dengan urutan baru
            q.pilihan_a = pilihan_list[0][1]
            q.pilihan_b = pilihan_list[1][1]
            q.pilihan_c = pilihan_list[2][1]
            q.pilihan_d = pilihan_list[3][1]
            
            # Cari jawaban benar di posisi baru
            new_answer_position = None
            for i, (orig_letter, answer_text) in enumerate(pilihan_list):
                if answer_text == correct_answer_text:
                    new_answer_position = chr(ord('A') + i)
                    break
            
            if new_answer_position:
                q.jawaban_benar = new_answer_position
            
            fixed_count += 1
        
        # Commit perubahan
        try:
            db.session.commit()
            print(f"✓ Berhasil memperbaiki {fixed_count} soal huruf")
            print(f"\nPerubahan yang dilakukan:")
            print(f"  1. Menambahkan opsi D untuk soal yang kosong")
            print(f"  2. Mengacak urutan pilihan A, B, C, D")
            print(f"  3. Memperbarui jawaban benar sesuai urutan baru\n")
            
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ GAGAL: {str(e)}\n")
            return False

if __name__ == '__main__':
    success = fix_huruf_questions()
    sys.exit(0 if success else 1)
