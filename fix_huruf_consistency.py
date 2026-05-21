#!/usr/bin/env python3
"""
Script untuk memperbaiki soal huruf yang tidak konsisten.
Memastikan soal-soal tetap valid setelah penyeimbangan.
"""

import sys
import os
import re

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.question import Soal

app = create_app()

def fix_initial_letter_consistency():
    """
    Memperbaiki soal tipe 'initial_letter' agar jawaban yang benar
    selalu dimulai dengan huruf yang benar sesuai pertanyaan.
    """
    with app.app_context():
        soal_initial = Soal.query.filter_by(question_type='initial_letter').all()
        
        print(f"Memperbaiki {len(soal_initial)} soal tipe 'initial_letter'")
        print("="*80)
        
        fixed = 0
        for idx, soal in enumerate(soal_initial, 1):
            # Ekstrak huruf dari pertanyaan
            # Contoh: "Pilih gambar yang diawali huruf A."
            match = re.search(r"huruf ([A-Z])", soal.pertanyaan, re.IGNORECASE)
            if not match:
                continue
            
            expected_letter = match.group(1).upper()
            
            # Ambil opsi
            opsi = {
                'A': (soal.pilihan_a or '').strip(),
                'B': (soal.pilihan_b or '').strip(),
                'C': (soal.pilihan_c or '').strip(),
                'D': (soal.pilihan_d or '').strip(),
            }
            
            # Cari opsi yang dimulai dengan huruf yang benar
            correct_options = {pos: opt for pos, opt in opsi.items() 
                             if opt and opt[0].upper() == expected_letter}
            
            if not correct_options:
                print(f"Soal {idx}: TIDAK BISA - tidak ada opsi yang dimulai dengan {expected_letter}")
                continue
            
            # Ambil salah satu opsi yang benar secara acak
            import random
            new_answer_pos = random.choice(list(correct_options.keys()))
            correct_answer = correct_options[new_answer_pos]
            
            # Jika jawaban benar sudah di posisi yang benar, lanjut
            if soal.jawaban_benar == new_answer_pos:
                continue
            
            # Swap opsi agar jawaban benar ada di posisi yang baru
            old_answer_pos = soal.jawaban_benar
            old_answer = opsi[old_answer_pos]
            
            # Update
            setattr(soal, f'pilihan_{old_answer_pos.lower()}', opsi[new_answer_pos])
            setattr(soal, f'pilihan_{new_answer_pos.lower()}', old_answer)
            soal.jawaban_benar = new_answer_pos
            
            fixed += 1
            if fixed <= 5 or fixed % 10 == 0:
                print(f"Soal {idx}: Diperbaiki - jawaban {old_answer_pos} → {new_answer_pos}")
        
        print(f"\n✓ {fixed} soal tipe 'initial_letter' diperbaiki")
        
        # Simpan
        if fixed > 0:
            db.session.commit()
            print(f"✓ Perubahan tersimpan ke database")
        
        return fixed

def verify_consistency():
    """
    Memverifikasi konsistensi semua soal.
    """
    with app.app_context():
        soal_initial = Soal.query.filter_by(question_type='initial_letter').all()
        
        print(f"\nVerifikasi {len(soal_initial)} soal tipe 'initial_letter'")
        print("="*80)
        
        issues = []
        valid = 0
        
        for idx, soal in enumerate(soal_initial, 1):
            # Ekstrak huruf dari pertanyaan
            match = re.search(r"huruf ([A-Z])", soal.pertanyaan, re.IGNORECASE)
            if not match:
                continue
            
            expected_letter = match.group(1).upper()
            
            # Ambil jawaban
            opsi = {
                'A': (soal.pilihan_a or '').strip(),
                'B': (soal.pilihan_b or '').strip(),
                'C': (soal.pilihan_c or '').strip(),
                'D': (soal.pilihan_d or '').strip(),
            }
            
            answer_text = opsi[soal.jawaban_benar]
            
            # Cek apakah jawaban dimulai dengan huruf yang benar
            if answer_text and answer_text[0].upper() == expected_letter:
                valid += 1
            else:
                issues.append(f"Soal {idx}: Jawaban '{answer_text}' tidak dimulai dengan '{expected_letter}'")
        
        print(f"Valid: {valid}/{len(soal_initial)}")
        if issues:
            print(f"\n⚠️  {len(issues)} masalah:")
            for issue in issues[:5]:
                print(f"  {issue}")
            if len(issues) > 5:
                print(f"  ... dan {len(issues) - 5} lagi")
        else:
            print(f"\n✓ Semua soal konsisten!")

if __name__ == '__main__':
    print("PERBAIKAN KONSISTENSI SOAL HURUF")
    print("="*80)
    
    fixed = fix_initial_letter_consistency()
    verify_consistency()
    
    print("\n" + "="*80)
    print("Perbaikan selesai")
