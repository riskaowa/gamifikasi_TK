#!/usr/bin/env python3
"""
Script untuk memverifikasi kevalidan soal-soal huruf setelah penyeimbangan.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.question import Soal
from collections import defaultdict

app = create_app()

def verify_huruf_questions():
    with app.app_context():
        # Ambil semua soal huruf
        soal_huruf = Soal.query.filter_by(kategori='huruf').all()
        
        print("VERIFIKASI SOAL HURUF")
        print("="*80)
        
        issues = []
        valid_count = 0
        samples_by_type = defaultdict(list)
        
        for idx, soal in enumerate(soal_huruf, 1):
            # Validasi jawaban
            if not soal.jawaban_benar or soal.jawaban_benar not in ['A', 'B', 'C', 'D']:
                issues.append(f"Soal {idx}: Jawaban benar tidak valid '{soal.jawaban_benar}'")
                continue
            
            # Validasi opsi
            opsi = {
                'A': (soal.pilihan_a or '').strip(),
                'B': (soal.pilihan_b or '').strip(),
                'C': (soal.pilihan_c or '').strip(),
                'D': (soal.pilihan_d or '').strip(),
            }
            
            if not all(opsi.values()):
                issues.append(f"Soal {idx}: Tidak semua 4 opsi terisi")
                continue
            
            # Validasi jawaban ada di opsi
            answer_text = opsi[soal.jawaban_benar]
            if not answer_text:
                issues.append(f"Soal {idx}: Jawaban benar tidak ada di pilihan")
                continue
            
            # Validasi duplikasi
            unique_opsi = set(v.lower() for v in opsi.values())
            if len(unique_opsi) < 4:
                issues.append(f"Soal {idx}: Ada duplikasi opsi")
                continue
            
            # Cek konsistensi jawaban dengan soal
            question_type = soal.question_type
            
            # Untuk tipe initial_letter, jawaban harus berupa kata
            if question_type == 'initial_letter':
                # Jawaban seharusnya dimulai dengan huruf
                try:
                    # Ambil huruf pertama dari pertanyaan
                    import re
                    match = re.search(r"huruf ([A-Z])", soal.pertanyaan, re.IGNORECASE)
                    if match:
                        expected_letter = match.group(1).upper()
                        answer_first_letter = answer_text[0].upper()
                        if answer_first_letter != expected_letter:
                            issues.append(f"Soal {idx}: Jawaban tidak dimulai dengan huruf {expected_letter}")
                            continue
                except Exception as e:
                    pass
            
            valid_count += 1
            
            # Simpan sample untuk ditampilkan
            if len(samples_by_type[question_type]) < 2:
                samples_by_type[question_type].append({
                    'id': soal.id,
                    'pertanyaan': soal.pertanyaan,
                    'opsi': opsi,
                    'jawaban': soal.jawaban_benar,
                    'answer_text': answer_text,
                    'type': question_type
                })
        
        # Laporan
        print(f"\nTotal soal: {len(soal_huruf)}")
        print(f"Valid: {valid_count}")
        print(f"Issues: {len(issues)}")
        
        if issues:
            print("\n⚠️  Masalah yang ditemukan:")
            for issue in issues[:10]:
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... dan {len(issues) - 10} masalah lainnya")
        else:
            print("\n✓ Semua soal valid dan sesuai!")
        
        # Tampilkan sample
        print("\n" + "="*80)
        print("SAMPLE SOAL")
        print("="*80)
        
        for qtype, samples in sorted(samples_by_type.items()):
            for sample in samples:
                print(f"\nTipe: {qtype}")
                print(f"Pertanyaan: {sample['pertanyaan']}")
                print(f"Opsi A: {sample['opsi']['A']}")
                print(f"Opsi B: {sample['opsi']['B']}")
                print(f"Opsi C: {sample['opsi']['C']}")
                print(f"Opsi D: {sample['opsi']['D']}")
                print(f"Jawaban: {sample['jawaban']} - {sample['answer_text']}")
                print("-"*80)
        
        print("\n✓ Verifikasi selesai")

if __name__ == '__main__':
    verify_huruf_questions()
