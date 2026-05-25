#!/usr/bin/env python3
"""
Fix huruf questions where image_question displays the wrong letter.

Issue: 127 out of 153 huruf questions have image_question displaying the wrong letter,
while jawaban_benar points to a different letter.

Example: Question 807 displays 'M' but jawaban_benar='C' which points to 'N'.
This causes users to see M but selecting M is marked wrong; selecting N is correct.

Solution: Regenerate image_question to display the correct answer text.
"""

import sys
import sqlite3
from pathlib import Path
from urllib.parse import unquote, quote
import re

sys.path.insert(0, str(Path(__file__).parent / 'gamifikasi-paud-main'))

from app import create_app, db
from app.models.question import Soal
from app.routes import _build_visual_image_data

app = create_app()

def extract_displayed_text(image_question):
    """Extract the displayed text from SVG image_question."""
    if not image_question or not image_question.startswith('data:image/svg+xml;utf8,'):
        return None
    
    svg = unquote(image_question.split(',', 1)[1])
    texts = re.findall(r'<text[^>]*>([^<]+)</text>', svg)
    return texts[0] if texts else None

def fix_huruf_images():
    """Fix all huruf questions with image mismatches."""
    
    with app.app_context():
        # Get all huruf questions with SVG images
        questions = Soal.query.filter(
            Soal.kategori == 'huruf',
            Soal.image_question.isnot(None)
        ).all()
        
        mismatches_found = 0
        mismatches_fixed = 0
        
        for question in questions:
            # Get the correct answer text
            answer_key = question.jawaban_benar.upper() if question.jawaban_benar else None
            if answer_key not in {'A', 'B', 'C', 'D'}:
                continue
            
            # Map answer key to the correct option
            option_map = {
                'A': (question.pilihan_a or '').strip(),
                'B': (question.pilihan_b or '').strip(),
                'C': (question.pilihan_c or '').strip(),
                'D': (question.pilihan_d or '').strip(),
            }
            
            correct_answer_text = option_map.get(answer_key, '')
            if not correct_answer_text:
                continue
            
            # Check what's currently displayed
            displayed = extract_displayed_text(question.image_question)
            
            # If it doesn't match, we need to fix it
            if displayed != correct_answer_text:
                mismatches_found += 1
                
                # Generate correct image
                new_image = _build_visual_image_data(correct_answer_text, question.kategori)
                
                if new_image and new_image != question.image_question:
                    question.image_question = new_image
                    db.session.add(question)
                    mismatches_fixed += 1
                    
                    print(f"✓ Fixed ID {question.id} ({question.question_type})")
                    print(f"  Was displaying: {displayed} -> Now: {correct_answer_text}")
        
        # Commit all changes
        if mismatches_fixed > 0:
            db.session.commit()
            print(f"\n✓ Successfully fixed {mismatches_fixed} questions")
        
        print(f"\nSummary:")
        print(f"  Mismatches found: {mismatches_found}")
        print(f"  Mismatches fixed: {mismatches_fixed}")

if __name__ == '__main__':
    print("Fixing huruf questions with image display mismatches...\n")
    fix_huruf_images()
    print("\nDone!")
