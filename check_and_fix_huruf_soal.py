#!/usr/bin/env python3
"""
Script untuk memeriksa dan memperbaiki soal-soal huruf.
Memastikan:
1. Setiap soal memiliki 4 opsi pilihan
2. 1 jawaban benar dari 4 opsi
3. Jawaban benar tersebar di semua posisi (A, B, C, D)
4. Tidak ada duplikasi opsi dalam satu soal
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.question import Soal
import random

app = create_app()

def check_and_fix_huruf_questions():
    with app.app_context():
        # Ambil semua soal huruf
        soal_huruf = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"Total soal huruf: {len(soal_huruf)}")
        print("-" * 80)
        
        # Statistik jawaban
        answer_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        issues = []
        fixed = 0
        
        for idx, soal in enumerate(soal_huruf, 1):
            # Check jawaban benar
            if not soal.jawaban_benar or soal.jawaban_benar not in ['A', 'B', 'C', 'D']:
                issues.append(f"Soal {idx}: Jawaban tidak valid '{soal.jawaban_benar}'")
                continue
            
            # Check opsi
            opsi = [soal.pilihan_a, soal.pilihan_b, soal.pilihan_c, soal.pilihan_d]
            if not all(opsi):
                issues.append(f"Soal {idx}: Tidak semua 4 opsi terisi")
                continue
            
            # Check duplikasi opsi
            unique_opsi = set(opt.strip().lower() if opt else '' for opt in opsi)
            if len(unique_opsi) < 4:
                # Ada duplikasi, perlu diperbaiki
                print(f"\n[PERBAIKAN] Soal {idx}:")
                print(f"  Pertanyaan: {soal.pertanyaan}")
                print(f"  Opsi A: {soal.pilihan_a}")
                print(f"  Opsi B: {soal.pilihan_b}")
                print(f"  Opsi C: {soal.pilihan_c}")
                print(f"  Opsi D: {soal.pilihan_d}")
                print(f"  Jawaban: {soal.jawaban_benar}")
                print(f"  → Ada duplikasi opsi, mencoba memperbaiki...")
                
                # Coba buat opsi yang berbeda
                answer_key = soal.jawaban_benar
                answer_text = soal.pilihan_a if answer_key == 'A' else \
                             soal.pilihan_b if answer_key == 'B' else \
                             soal.pilihan_c if answer_key == 'C' else soal.pilihan_d
                
                # Generate opsi alternatif untuk huruf
                if len(answer_text) == 1 and answer_text.isalpha():
                    letter = answer_text.upper()
                    letters = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
                    idx_letter = letters.index(letter)
                    
                    wrong_letters = [
                        letters[(idx_letter - 1) % 26],
                        letters[(idx_letter + 1) % 26],
                        letters[(idx_letter + 5) % 26]
                    ]
                    
                    # Acak opsi
                    all_options = [answer_text] + wrong_letters
                    random.shuffle(all_options)
                    
                    # Temukan posisi jawaban setelah acak
                    new_position = all_options.index(answer_text.upper())
                    new_answer = ['A', 'B', 'C', 'D'][new_position]
                    
                    # Update
                    soal.pilihan_a = all_options[0]
                    soal.pilihan_b = all_options[1]
                    soal.pilihan_c = all_options[2]
                    soal.pilihan_d = all_options[3]
                    soal.jawaban_benar = new_answer
                    
                    print(f"  ✓ Diperbaiki:")
                    print(f"    Opsi A: {soal.pilihan_a}, Opsi B: {soal.pilihan_b}, Opsi C: {soal.pilihan_c}, Opsi D: {soal.pilihan_d}")
                    print(f"    Jawaban: {soal.jawaban_benar}")
                    fixed += 1
            
            answer_counts[soal.jawaban_benar] += 1
        
        # Laporan
        print("\n" + "="*80)
        print("LAPORAN ANALISIS")
        print("="*80)
        print(f"\nDistribusi Jawaban Benar:")
        for answer, count in sorted(answer_counts.items()):
            percentage = (count / len(soal_huruf)) * 100 if soal_huruf else 0
            print(f"  {answer}: {count:3d} ({percentage:5.1f}%)")
        
        if issues:
            print(f"\n⚠️  Ditemukan {len(issues)} masalah:")
            for issue in issues[:10]:
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... dan {len(issues) - 10} masalah lainnya")
        
        print(f"\n✓ Diperbaiki: {fixed} soal")
        
        # Simpan perubahan
        if fixed > 0:
            db.session.commit()
            print(f"✓ Perubahan tersimpan ke database")
        
        return {
            'total': len(soal_huruf),
            'answer_distribution': answer_counts,
            'issues': len(issues),
            'fixed': fixed
        }

if __name__ == '__main__':
    result = check_and_fix_huruf_questions()
    print("\n" + "="*80)
    print("Analisis selesai")
