#!/usr/bin/env python3
"""
Script untuk memverifikasi kevalidan soal huruf yang baru dibuat.
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

def verify_all_huruf_questions():
    with app.app_context():
        soal_huruf = Soal.query.filter_by(kategori='huruf').all()
        
        print("VERIFIKASI SOAL HURUF BARU")
        print("="*80)
        
        print(f"\nTotal soal: {len(soal_huruf)}")
        
        issues = []
        valid = 0
        samples = []
        
        for idx, soal in enumerate(soal_huruf, 1):
            # Check jawaban valid
            if not soal.jawaban_benar or soal.jawaban_benar not in ['A', 'B', 'C', 'D']:
                issues.append(f"Soal {idx}: Jawaban tidak valid")
                continue
            
            # Check semua opsi ada
            opsi = {
                'A': (soal.pilihan_a or '').strip(),
                'B': (soal.pilihan_b or '').strip(),
                'C': (soal.pilihan_c or '').strip(),
                'D': (soal.pilihan_d or '').strip(),
            }
            
            if not all(opsi.values()):
                issues.append(f"Soal {idx}: Tidak semua 4 opsi terisi")
                continue
            
            # Check jawaban ada di opsi
            answer_text = opsi[soal.jawaban_benar]
            if not answer_text:
                issues.append(f"Soal {idx}: Jawaban tidak ada di pilihan")
                continue
            
            # Check opsi unik
            unique = set(v.lower() for v in opsi.values())
            if len(unique) < 4:
                issues.append(f"Soal {idx}: Ada duplikasi opsi")
                continue
            
            # Check consistency untuk initial_letter
            if soal.question_type == 'initial_letter':
                match = re.search(r"huruf ([A-Z])", soal.pertanyaan, re.IGNORECASE)
                if match:
                    expected_letter = match.group(1).upper()
                    if not answer_text or answer_text[0].upper() != expected_letter:
                        issues.append(f"Soal {idx}: Jawaban tidak dimulai dengan {expected_letter}")
                        continue
            
            valid += 1
            
            # Simpan sample
            if len(samples) < 6:
                samples.append({
                    'no': idx,
                    'type': soal.question_type,
                    'pertanyaan': soal.pertanyaan,
                    'opsi': opsi,
                    'jawaban': soal.jawaban_benar,
                    'answer_text': answer_text
                })
        
        # Laporan
        print(f"✓ Valid: {valid}/{len(soal_huruf)}")
        if issues:
            print(f"⚠️  Issues: {len(issues)}")
            for issue in issues[:5]:
                print(f"  - {issue}")
        else:
            print(f"✓ Semua soal valid!")
        
        # Sample
        print("\n" + "="*80)
        print("SAMPLE SOAL (6 soal pertama)")
        print("="*80)
        
        for sample in samples:
            print(f"\nSoal {sample['no']} ({sample['type']}):")
            print(f"  Pertanyaan: {sample['pertanyaan']}")
            print(f"  A. {sample['opsi']['A']}")
            print(f"  B. {sample['opsi']['B']}")
            print(f"  C. {sample['opsi']['C']}")
            print(f"  D. {sample['opsi']['D']}")
            print(f"  Jawaban: {sample['jawaban']} - {sample['answer_text']}")
        
        # Distribusi
        print("\n" + "="*80)
        print("DISTRIBUSI JAWABAN")
        print("="*80)
        
        from collections import defaultdict
        by_type = defaultdict(lambda: {'A': 0, 'B': 0, 'C': 0, 'D': 0})
        total_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for soal in soal_huruf:
            by_type[soal.question_type][soal.jawaban_benar] += 1
            total_dist[soal.jawaban_benar] += 1
        
        for qtype in sorted(by_type.keys()):
            print(f"\n{qtype}:")
            count = sum(by_type[qtype].values())
            for answer in ['A', 'B', 'C', 'D']:
                cnt = by_type[qtype][answer]
                pct = (cnt / count) * 100 if count > 0 else 0
                print(f"  {answer}: {cnt:2d}/{count} ({pct:5.1f}%)")
        
        print(f"\nTOTAL:")
        for answer in ['A', 'B', 'C', 'D']:
            cnt = total_dist[answer]
            pct = (cnt / len(soal_huruf)) * 100
            print(f"  {answer}: {cnt:2d}/{len(soal_huruf)} ({pct:5.1f}%)")
        
        return {
            'total': len(soal_huruf),
            'valid': valid,
            'issues': len(issues)
        }

if __name__ == '__main__':
    result = verify_all_huruf_questions()
    print("\n" + "="*80)
    if result['issues'] == 0:
        print("✓ VERIFIKASI SELESAI - SEMUA SOAL VALID")
    else:
        print(f"⚠️  VERIFIKASI SELESAI - {result['issues']} MASALAH DITEMUKAN")
