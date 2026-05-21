#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk memverifikasi soal huruf yang tersisa.
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
    for char in text:
        if char.isalpha():
            return char
    return None

def get_correct_answer_text(question):
    """Get the text of the correct answer choice."""
    answer_map = {
        'A': question.pilihan_a,
        'B': question.pilihan_b,
        'C': question.pilihan_c,
        'D': question.pilihan_d,
    }
    answer_letter = question.jawaban_benar.upper()
    return answer_map.get(answer_letter, None)

def verify_remaining_soals(app):
    """Verify remaining huruf soals are consistent."""
    
    with app.app_context():
        huruf_soals = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"VERIFIKASI SOAL HURUF YANG TERSISA")
        print(f"{'='*80}\n")
        print(f"Total soal huruf: {len(huruf_soals)}\n")
        
        if len(huruf_soals) == 0:
            print("❌ Tidak ada soal huruf tersisa!")
            return
        
        all_consistent = True
        
        for i, soal in enumerate(huruf_soals, 1):
            correct_answer_text = get_correct_answer_text(soal)
            correct_answer_letter = extract_letter_from_choice(correct_answer_text)
            expected_answer_letter = soal.jawaban_benar.upper()
            
            is_consistent = correct_answer_letter == expected_answer_letter
            status = "✅ OK" if is_consistent else "❌ ERROR"
            
            print(f"{i}. ID {soal.id}: {status}")
            print(f"   Pertanyaan: {soal.pertanyaan[:60]}...")
            print(f"   Jawaban: {expected_answer_letter}")
            print(f"   Pilihan:")
            print(f"     A: {soal.pilihan_a}")
            print(f"     B: {soal.pilihan_b}")
            print(f"     C: {soal.pilihan_c}")
            print(f"     D: {soal.pilihan_d}")
            print()
            
            if not is_consistent:
                all_consistent = False
        
        print(f"{'='*80}")
        if all_consistent:
            print("✅ SEMUA SOAL HURUF KONSISTEN!")
        else:
            print("❌ Ada soal yang masih bermasalah!")
        print(f"{'='*80}\n")

if __name__ == '__main__':
    app = create_app()
    verify_remaining_soals(app)
