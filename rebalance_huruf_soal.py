#!/usr/bin/env python3
"""
Script untuk menyeimbangkan distribusi jawaban benar soal huruf.
Memastikan jawaban benar tersebar merata di semua posisi (A, B, C, D).
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
from collections import defaultdict

app = create_app()

def rebalance_huruf_questions():
    with app.app_context():
        # Ambil semua soal huruf
        soal_huruf = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"Total soal huruf: {len(soal_huruf)}")
        print("-" * 80)
        
        # Kelompokkan soal berdasarkan tipe
        soal_by_type = defaultdict(list)
        for soal in soal_huruf:
            soal_by_type[soal.question_type].append(soal)
        
        print("\nSoal berdasarkan tipe:")
        for qtype, soals in sorted(soal_by_type.items()):
            print(f"  {qtype}: {len(soals)} soal")
        
        # Hitung distribusi saat ini
        current_distribution = defaultdict(lambda: defaultdict(int))
        for soal in soal_huruf:
            current_distribution[soal.question_type][soal.jawaban_benar] += 1
        
        print("\n" + "="*80)
        print("DISTRIBUSI JAWABAN SAAT INI")
        print("="*80)
        for qtype in sorted(soal_by_type.keys()):
            print(f"\n{qtype}:")
            total = len(soal_by_type[qtype])
            for answer in ['A', 'B', 'C', 'D']:
                count = current_distribution[qtype][answer]
                pct = (count / total) * 100 if total > 0 else 0
                print(f"  {answer}: {count:2d}/{total} ({pct:5.1f}%)")
        
        # Buat target distribusi yang lebih merata
        print("\n" + "="*80)
        print("PENYEIMBANGAN JAWABAN")
        print("="*80)
        
        modified = 0
        for qtype, soals in soal_by_type.items():
            if not soals:
                continue
            
            total = len(soals)
            target_per_answer = total // 4
            extra = total % 4
            
            # Tentukan berapa soal untuk setiap jawaban
            targets = {
                'A': target_per_answer + (1 if i < extra else 0) for i in range(extra)
            }
            targets = {'A': target_per_answer, 'B': target_per_answer, 'C': target_per_answer, 'D': target_per_answer}
            if extra > 0:
                targets['A'] += 1
            if extra > 1:
                targets['B'] += 1
            if extra > 2:
                targets['C'] += 1
            
            print(f"\n{qtype} (total: {total}):")
            print(f"  Target per jawaban: {target_per_answer}")
            print(f"  Target: A={targets['A']}, B={targets['B']}, C={targets['C']}, D={targets['D']}")
            
            # Kelompokkan soal per jawaban saat ini
            soals_by_answer = defaultdict(list)
            for soal in soals:
                soals_by_answer[soal.jawaban_benar].append(soal)
            
            # Acak dan distribusikan ulang
            all_soals = list(soals)
            random.shuffle(all_soals)
            
            answer_sequence = ['A', 'B', 'C', 'D']
            if extra > 0:
                answer_sequence = ['A', 'B', 'C', 'D'] * (total // 4)
                answer_sequence = (answer_sequence + ['A', 'B', 'C'][:extra])[:total]
                random.shuffle(answer_sequence)
            else:
                answer_sequence = (['A', 'B', 'C', 'D'] * (total // 4))
                random.shuffle(answer_sequence)
            
            # Terapkan jawaban baru
            modified_in_type = 0
            for idx, soal in enumerate(all_soals):
                new_answer = answer_sequence[idx % len(answer_sequence)]
                
                if new_answer != soal.jawaban_benar:
                    # Pindahkan jawaban benar ke posisi baru
                    old_answer = soal.jawaban_benar
                    
                    # Swap opsi
                    option_names = ['pilihan_a', 'pilihan_b', 'pilihan_c', 'pilihan_d']
                    old_pos = ord(old_answer) - ord('A')
                    new_pos = ord(new_answer) - ord('A')
                    
                    # Ambil nilai
                    old_value = getattr(soal, option_names[old_pos])
                    new_value = getattr(soal, option_names[new_pos])
                    
                    # Swap
                    setattr(soal, option_names[old_pos], new_value)
                    setattr(soal, option_names[new_pos], old_value)
                    soal.jawaban_benar = new_answer
                    
                    modified_in_type += 1
            
            print(f"  → {modified_in_type} soal dimodifikasi")
            modified += modified_in_type
        
        # Verifikasi hasil
        print("\n" + "="*80)
        print("DISTRIBUSI JAWABAN SETELAH PENYEIMBANGAN")
        print("="*80)
        
        new_distribution = defaultdict(lambda: defaultdict(int))
        for soal in soal_huruf:
            new_distribution[soal.question_type][soal.jawaban_benar] += 1
        
        total_new = defaultdict(int)
        for qtype in sorted(soal_by_type.keys()):
            print(f"\n{qtype}:")
            total = len(soal_by_type[qtype])
            for answer in ['A', 'B', 'C', 'D']:
                count = new_distribution[qtype][answer]
                pct = (count / total) * 100 if total > 0 else 0
                print(f"  {answer}: {count:2d}/{total} ({pct:5.1f}%)")
                total_new[answer] += count
        
        # Total keseluruhan
        print("\n" + "-"*80)
        print("TOTAL KESELURUHAN:")
        for answer in ['A', 'B', 'C', 'D']:
            count = total_new[answer]
            pct = (count / len(soal_huruf)) * 100
            print(f"  {answer}: {count:2d}/{len(soal_huruf)} ({pct:5.1f}%)")
        
        # Simpan perubahan
        if modified > 0:
            db.session.commit()
            print(f"\n✓ {modified} soal dimodifikasi dan perubahan tersimpan ke database")
        else:
            print(f"\n✓ Tidak ada perubahan diperlukan")
        
        return {
            'total': len(soal_huruf),
            'modified': modified
        }

if __name__ == '__main__':
    result = rebalance_huruf_questions()
    print("\n" + "="*80)
    print("Penyeimbangan selesai")
