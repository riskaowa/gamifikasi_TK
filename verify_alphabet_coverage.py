#!/usr/bin/env python3
"""
Script untuk memverifikasi bahwa soal-soal huruf mencakup semua huruf A-Z
dan tidak hanya A semata.
"""

import sys
import os
import re
from collections import defaultdict

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.question import Soal

app = create_app()

def verify_alphabet_coverage():
    with app.app_context():
        soal_huruf = Soal.query.filter_by(kategori='huruf').all()
        
        print("VERIFIKASI CAKUPAN HURUF A-Z")
        print("="*80)
        
        # Ekstrak huruf dari pertanyaan atau jawaban
        huruf_found = set()
        huruf_by_type = defaultdict(set)
        
        for soal in soal_huruf:
            # Cari huruf di pertanyaan (dengan regex)
            pertanyaan = soal.pertanyaan or ""
            
            # Contoh: "Huruf apakah ini: A?" atau "Setelah huruf A adalah"
            match_huruf = re.findall(r'huruf\s+([A-Z])', pertanyaan, re.IGNORECASE)
            for huruf in match_huruf:
                huruf_found.add(huruf.upper())
                huruf_by_type[soal.question_type].add(huruf.upper())
            
            # Jika tidak ada di pertanyaan, coba di jawaban/opsi
            if not match_huruf:
                jawaban_text = soal.pilihan_a or soal.pilihan_b or soal.pilihan_c or soal.pilihan_d
                match_huruf = re.findall(r'^([A-Z])$', jawaban_text or "", re.IGNORECASE)
                for huruf in match_huruf:
                    huruf_found.add(huruf.upper())
                    huruf_by_type[soal.question_type].add(huruf.upper())
        
        # Verifikasi cakupan A-Z
        alphabet = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        missing = alphabet - huruf_found
        
        print(f"\nTotal soal: {len(soal_huruf)}")
        print(f"Huruf yang ditemukan: {len(huruf_found)}")
        print(f"Cakupan: {', '.join(sorted(huruf_found))}")
        
        if missing:
            print(f"\n⚠️  Huruf yang TIDAK ditemukan: {', '.join(sorted(missing))}")
        else:
            print(f"\n✓ SEMUA HURUF A-Z TERCAKUP!")
        
        # Analisis per tipe soal
        print(f"\n" + "="*80)
        print("CAKUPAN PER TIPE SOAL")
        print("="*80)
        
        for qtype in sorted(huruf_by_type.keys()):
            huruf = sorted(huruf_by_type[qtype])
            count = len(huruf)
            print(f"\n{qtype}: {count}/26 huruf")
            print(f"  Huruf: {', '.join(huruf)}")
        
        # Tampilkan beberapa contoh soal dari huruf yang berbeda
        print(f"\n" + "="*80)
        print("CONTOH SOAL DARI BERBAGAI HURUF")
        print("="*80)
        
        huruf_examples = {}
        for soal in soal_huruf:
            pertanyaan = soal.pertanyaan or ""
            match_huruf = re.findall(r'huruf\s+([A-Z])', pertanyaan, re.IGNORECASE)
            
            for huruf in match_huruf:
                huruf = huruf.upper()
                if huruf not in huruf_examples:
                    huruf_examples[huruf] = soal
        
        for huruf in sorted(huruf_examples.keys())[:10]:
            soal = huruf_examples[huruf]
            print(f"\n{huruf}:")
            print(f"  Tipe: {soal.question_type}")
            print(f"  Pertanyaan: {soal.pertanyaan}")
            print(f"  Opsi: A={soal.pilihan_a}, B={soal.pilihan_b}, C={soal.pilihan_c}, D={soal.pilihan_d}")
            print(f"  Jawaban: {soal.jawaban_benar}")

if __name__ == '__main__':
    verify_alphabet_coverage()
    print("\n" + "="*80)
    print("✓ Verifikasi selesai")
