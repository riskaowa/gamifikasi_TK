#!/usr/bin/env python3
"""
Script untuk menganalisis dan membersihkan soal huruf B dan Z yang bermasalah.
Menampilkan soal-soal yang memiliki jawaban benar yang tidak sesuai.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def extract_letter_from_choice(choice_text):
    """Extract single letter from choice text."""
    if not choice_text:
        return None
    text = str(choice_text).strip().upper()
    # Ambil huruf pertama yang ditemukan
    for char in text:
        if char.isalpha():
            return char
    return None

def analyze_b_z_issues():
    """Analisis soal huruf B dan Z yang bermasalah."""
    
    app = create_app()
    
    with app.app_context():
        # Ambil semua soal kategori huruf
        huruf_questions = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"ANALISIS SOAL HURUF B DAN Z YANG BERMASALAH")
        print(f"{'='*80}\n")
        print(f"Total soal huruf: {len(huruf_questions)}\n")
        
        b_problems = []
        z_problems = []
        
        for q in huruf_questions:
            pertanyaan_lower = q.pertanyaan.lower()
            correct_letter = q.jawaban_benar.upper()
            
            # Ambil pilihan jawaban
            options = {
                'A': q.pilihan_a,
                'B': q.pilihan_b,
                'C': q.pilihan_c,
                'D': q.pilihan_d,
            }
            
            # Ekstrak huruf dari setiap pilihan
            extracted_letters = {
                k: extract_letter_from_choice(v) 
                for k, v in options.items()
            }
            
            # Deteksi soal tentang huruf B
            if 'pilih huruf b' in pertanyaan_lower or 'huruf b' in pertanyaan_lower:
                # Soal tentang B seharusnya jawaban B
                if correct_letter != 'B':
                    b_problems.append({
                        'id': q.id,
                        'pertanyaan': q.pertanyaan,
                        'options': options,
                        'extracted': extracted_letters,
                        'jawaban_db': correct_letter,
                        'seharusnya': 'B'
                    })
            
            # Deteksi soal tentang huruf Z
            elif 'pilih huruf z' in pertanyaan_lower or 'huruf z' in pertanyaan_lower:
                # Soal tentang Z seharusnya jawaban memiliki Z
                # Cari di mana Z berada
                z_location = None
                for letter_key, extracted_letter in extracted_letters.items():
                    if extracted_letter == 'Z':
                        z_location = letter_key
                        break
                
                # Jika jawaban DB tidak menunjuk ke pilihan yang berisi Z
                if z_location and correct_letter != z_location:
                    z_problems.append({
                        'id': q.id,
                        'pertanyaan': q.pertanyaan,
                        'options': options,
                        'extracted': extracted_letters,
                        'jawaban_db': correct_letter,
                        'seharusnya': z_location,
                        'z_location': z_location
                    })
        
        # Tampilkan hasil untuk B
        if b_problems:
            print(f"\n{'='*80}")
            print(f"SOAL HURUF B YANG BERMASALAH ({len(b_problems)} soal)")
            print(f"{'='*80}\n")
            for i, problem in enumerate(b_problems, 1):
                print(f"{i}. ID {problem['id']}")
                print(f"   Pertanyaan: {problem['pertanyaan']}")
                print(f"   A: {problem['options']['A']}")
                print(f"   B: {problem['options']['B']}")
                print(f"   C: {problem['options']['C']}")
                if problem['options']['D']:
                    print(f"   D: {problem['options']['D']}")
                print(f"   Jawaban di DB: {problem['jawaban_db']}")
                print(f"   Seharusnya: {problem['seharusnya']}")
                print()
        
        # Tampilkan hasil untuk Z
        if z_problems:
            print(f"\n{'='*80}")
            print(f"SOAL HURUF Z YANG BERMASALAH ({len(z_problems)} soal)")
            print(f"{'='*80}\n")
            for i, problem in enumerate(z_problems, 1):
                print(f"{i}. ID {problem['id']}")
                print(f"   Pertanyaan: {problem['pertanyaan']}")
                print(f"   A: {problem['options']['A']}")
                print(f"   B: {problem['options']['B']}")
                print(f"   C: {problem['options']['C']}")
                if problem['options']['D']:
                    print(f"   D: {problem['options']['D']}")
                print(f"   Jawaban di DB: {problem['jawaban_db']}")
                print(f"   Z terletak di: {problem['z_location']}")
                print(f"   Seharusnya: {problem['seharusnya']}")
                print()
        
        # Summary
        all_problems = b_problems + z_problems
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total soal B bermasalah: {len(b_problems)}")
        print(f"Total soal Z bermasalah: {len(z_problems)}")
        print(f"TOTAL SOAL BERMASALAH: {len(all_problems)}\n")
        
        if all_problems:
            print(f"ID-ID soal yang perlu dihapus:")
            print(f"{[p['id'] for p in all_problems]}")
        
        return {
            'b_problems': b_problems,
            'z_problems': z_problems,
            'all_ids': [p['id'] for p in all_problems]
        }

if __name__ == '__main__':
    results = analyze_b_z_issues()
