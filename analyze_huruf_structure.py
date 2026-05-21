#!/usr/bin/env python3
"""
Script untuk menganalisis struktur soal huruf dan melihat berapa banyak yang memiliki 3 atau 4 opsi.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def analyze_huruf_structure():
    """Analisis struktur soal huruf."""
    
    app = create_app()
    
    with app.app_context():
        huruf_questions = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"ANALISIS STRUKTUR SOAL HURUF")
        print(f"{'='*80}\n")
        print(f"Total soal huruf: {len(huruf_questions)}\n")
        
        # Hitung berdasarkan jumlah pilihan
        questions_with_3_options = []
        questions_with_4_options = []
        answer_distribution = {}
        
        for q in huruf_questions:
            # Hitung pilihan
            options = [q.pilihan_a, q.pilihan_b, q.pilihan_c, q.pilihan_d]
            num_options = sum(1 for opt in options if opt)
            
            if num_options == 3:
                questions_with_3_options.append(q)
            elif num_options == 4:
                questions_with_4_options.append(q)
            
            # Hitung distribusi jawaban
            answer = q.jawaban_benar.upper()
            answer_distribution[answer] = answer_distribution.get(answer, 0) + 1
        
        print(f"Soal dengan 3 opsi: {len(questions_with_3_options)}")
        print(f"Soal dengan 4 opsi: {len(questions_with_4_options)}\n")
        
        print(f"Distribusi jawaban benar:")
        for letter in ['A', 'B', 'C', 'D']:
            count = answer_distribution.get(letter, 0)
            percentage = (count / len(huruf_questions)) * 100
            print(f"  {letter}: {count} ({percentage:.1f}%)")
        
        print(f"\n{'='*80}")
        print(f"CONTOH SOAL DENGAN 3 OPSI (5 pertama):")
        print(f"{'='*80}\n")
        
        for i, q in enumerate(questions_with_3_options[:5], 1):
            print(f"{i}. ID {q.id}: {q.pertanyaan}")
            print(f"   A: {q.pilihan_a}")
            print(f"   B: {q.pilihan_b}")
            print(f"   C: {q.pilihan_c}")
            print(f"   D: {q.pilihan_d if q.pilihan_d else '(kosong)'}")
            print(f"   Jawaban: {q.jawaban_benar}\n")
        
        return {
            'with_3_options': questions_with_3_options,
            'with_4_options': questions_with_4_options,
            'answer_distribution': answer_distribution
        }

if __name__ == '__main__':
    analyze_huruf_structure()
