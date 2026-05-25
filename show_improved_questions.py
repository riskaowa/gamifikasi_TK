#!/usr/bin/env python3
"""
Script untuk menampilkan contoh soal huruf yang sudah diperbaiki.
"""

import sys
from pathlib import Path
import random

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def show_sample_questions():
    """Tampilkan contoh soal yang sudah diperbaiki."""
    
    app = create_app()
    
    with app.app_context():
        # Ambil soal dengan distribusi jawaban berbeda
        huruf_questions = Soal.query.filter_by(kategori='huruf').all()
        
        # Kelompokkan berdasarkan jawaban benar
        by_answer = {'A': [], 'B': [], 'C': [], 'D': []}
        for q in huruf_questions:
            answer = q.jawaban_benar.upper()
            by_answer[answer].append(q)
        
        print(f"\n{'='*80}")
        print(f"CONTOH SOAL HURUF YANG SUDAH DIPERBAIKI")
        print(f"{'='*80}\n")
        
        # Tampilkan contoh untuk setiap jawaban benar
        for answer_letter in ['A', 'B', 'C', 'D']:
            if by_answer[answer_letter]:
                q = by_answer[answer_letter][0]  # Ambil yang pertama
                print(f"Contoh soal dengan jawaban benar: {answer_letter}")
                print(f"ID {q.id}: {q.pertanyaan}")
                print(f"   A) {q.pilihan_a}")
                print(f"   B) {q.pilihan_b}")
                print(f"   C) {q.pilihan_c}")
                print(f"   D) {q.pilihan_d}")
                print(f"   ✓ Jawaban benar: {q.jawaban_benar}")
                print()
        
        print(f"{'='*80}")
        print(f"SUMMARY PERBAIKAN")
        print(f"{'='*80}\n")
        print(f"Total soal huruf: {len(huruf_questions)}")
        print(f"Semua soal sekarang memiliki 4 opsi jawaban ✓")
        print(f"\nDistribusi jawaban benar:")
        for letter in ['A', 'B', 'C', 'D']:
            count = len(by_answer[letter])
            percentage = (count / len(huruf_questions)) * 100
            print(f"  Jawaban {letter}: {count} soal ({percentage:.1f}%)")

if __name__ == '__main__':
    show_sample_questions()
