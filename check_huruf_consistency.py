#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk memeriksa dan memperbaiki soal huruf yang memiliki jawaban inconsistent.
"""

import os
import sys
from pathlib import Path

# Add the main app directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal

def extract_letter_from_choice(choice_text):
    """Extract single letter from choice text."""
    if not choice_text:
        return None
    # Get the first alphabetic character
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

def check_huruf_consistency(app):
    """Check and report huruf soal consistency issues."""
    
    with app.app_context():
        # Get all soal kategori huruf
        huruf_soals = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"PEMERIKSAAN SOAL HURUF - Total: {len(huruf_soals)} soal")
        print(f"{'='*80}\n")
        
        inconsistent_soals = []
        
        for soal in huruf_soals:
            correct_answer_text = get_correct_answer_text(soal)
            correct_answer_letter = extract_letter_from_choice(correct_answer_text)
            expected_answer_letter = soal.jawaban_benar.upper()
            
            # For letter matching games, the correct answer text should be the letter itself
            # Check if answer matches the letter that should be correct
            if correct_answer_letter and correct_answer_letter != expected_answer_letter:
                inconsistent_soals.append({
                    'id': soal.id,
                    'pertanyaan': soal.pertanyaan[:50],
                    'image': soal.image_question,
                    'jawaban_benar': expected_answer_letter,
                    'pilihan_a': soal.pilihan_a,
                    'pilihan_b': soal.pilihan_b,
                    'pilihan_c': soal.pilihan_c,
                    'pilihan_d': soal.pilihan_d,
                    'correct_text': correct_answer_text,
                    'expected_letter': expected_answer_letter,
                    'actual_letter': correct_answer_letter,
                })
        
        if inconsistent_soals:
            print(f"⚠️  DITEMUKAN {len(inconsistent_soals)} SOAL BERMASALAH:\n")
            for i, soal in enumerate(inconsistent_soals, 1):
                print(f"{i}. ID: {soal['id']}")
                print(f"   Pertanyaan: {soal['pertanyaan']}")
                print(f"   Jawaban benar (di DB): {soal['jawaban_benar']}")
                print(f"   Teks jawaban: {soal['correct_text']}")
                print(f"   Huruf dari teks: {soal['actual_letter']}")
                print(f"   Status: ❌ TIDAK SESUAI (seharusnya {soal['expected_letter']} tapi malah {soal['actual_letter']})")
                print(f"   Pilihan A: {soal['pilihan_a']}")
                print(f"   Pilihan B: {soal['pilihan_b']}")
                print(f"   Pilihan C: {soal['pilihan_c']}")
                print(f"   Pilihan D: {soal['pilihan_d']}")
                print()
            
            return inconsistent_soals
        else:
            print("✅ Semua soal huruf KONSISTEN - tidak ada masalah ditemukan!")
            return []

def delete_inconsistent_soals(app, soal_ids):
    """Delete inconsistent soals."""
    if not soal_ids:
        print("\nTidak ada soal yang dihapus.")
        return
    
    with app.app_context():
        print(f"\n{'='*80}")
        print(f"MENGHAPUS SOAL BERMASALAH - Total: {len(soal_ids)} soal")
        print(f"{'='*80}\n")
        
        for soal_id in soal_ids:
            soal = Soal.query.get(soal_id)
            if soal:
                print(f"Menghapus soal ID {soal_id}: {soal.pertanyaan[:50]}...")
                
                # Delete associated images if exist
                if soal.image_question:
                    image_path = os.path.join('app', 'static', 'uploads', 'question_bank', soal.image_question)
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            print(f"  ✓ Dihapus image: {soal.image_question}")
                        except Exception as e:
                            print(f"  ⚠️  Gagal hapus image: {e}")
                
                # Delete the soal record
                db.session.delete(soal)
        
        try:
            db.session.commit()
            print(f"\n✅ Berhasil menghapus {len(soal_ids)} soal!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat menghapus: {e}")

if __name__ == '__main__':
    app = create_app()
    
    # Check consistency
    inconsistent = check_huruf_consistency(app)
    
    # Ask for confirmation before deleting
    if inconsistent:
        print(f"\nJumlah soal bermasalah: {len(inconsistent)}")
        response = input("\nHapus soal-soal bermasalah ini? (y/n): ").strip().lower()
        if response == 'y':
            soal_ids = [s['id'] for s in inconsistent]
            delete_inconsistent_soals(app, soal_ids)
        else:
            print("Pembatalan - soal tidak dihapus.")
