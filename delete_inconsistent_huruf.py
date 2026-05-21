#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script untuk langsung menghapus soal huruf yang bermasalah.
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

def delete_inconsistent_huruf_soals(app):
    """Find and delete all inconsistent huruf soals."""
    
    with app.app_context():
        # Get all soal kategori huruf
        huruf_soals = Soal.query.filter_by(kategori='huruf').all()
        
        print(f"\n{'='*80}")
        print(f"PEMERIKSAAN DAN PENGHAPUSAN SOAL HURUF BERMASALAH")
        print(f"{'='*80}\n")
        print(f"Total soal huruf: {len(huruf_soals)}\n")
        
        inconsistent_ids = []
        
        for soal in huruf_soals:
            correct_answer_text = get_correct_answer_text(soal)
            correct_answer_letter = extract_letter_from_choice(correct_answer_text)
            expected_answer_letter = soal.jawaban_benar.upper()
            
            # Check if answer matches the letter that should be correct
            if correct_answer_letter and correct_answer_letter != expected_answer_letter:
                inconsistent_ids.append(soal.id)
        
        if not inconsistent_ids:
            print("✅ Semua soal huruf KONSISTEN - tidak ada yang perlu dihapus!")
            return
        
        print(f"⚠️  DITEMUKAN {len(inconsistent_ids)} SOAL BERMASALAH")
        print(f"Contoh soal bermasalah:")
        
        # Show first 5 examples
        for i, soal_id in enumerate(inconsistent_ids[:5], 1):
            soal = Soal.query.get(soal_id)
            correct_text = get_correct_answer_text(soal)
            correct_letter = extract_letter_from_choice(correct_text)
            print(f"{i}. ID {soal_id}: '{soal.pertanyaan[:40]}...' - "
                  f"Jawaban DB: {soal.jawaban_benar}, Teks: {correct_text} ({correct_letter})")
        
        if len(inconsistent_ids) > 5:
            print(f"... dan {len(inconsistent_ids) - 5} soal lainnya\n")
        else:
            print()
        
        # Delete all inconsistent soals
        print(f"{'='*80}")
        print(f"MENGHAPUS SOAL BERMASALAH...")
        print(f"{'='*80}\n")
        
        deleted_count = 0
        error_count = 0
        
        for soal_id in inconsistent_ids:
            soal = Soal.query.get(soal_id)
            if soal:
                try:
                    # Delete associated images if exist
                    if soal.image_question:
                        image_path = os.path.join('app', 'static', 'uploads', 'question_bank', soal.image_question)
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except Exception as e:
                                print(f"⚠️  Gagal hapus image {soal.image_question}: {e}")
                    
                    # Delete the soal record
                    db.session.delete(soal)
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"❌ Error saat hapus soal ID {soal_id}: {e}")
                    error_count += 1
        
        try:
            db.session.commit()
            print(f"\n{'='*80}")
            print(f"✅ SELESAI!")
            print(f"{'='*80}")
            print(f"✓ Soal dihapus: {deleted_count}")
            if error_count > 0:
                print(f"⚠️  Error: {error_count}")
            print(f"\nSisa soal huruf: {len(huruf_soals) - deleted_count}")
            print(f"{'='*80}\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat commit: {e}")

if __name__ == '__main__':
    app = create_app()
    delete_inconsistent_huruf_soals(app)
