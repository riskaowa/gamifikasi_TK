"""
Script untuk melihat beberapa soal huruf
"""

import sys
import os

# Adjust path to find app module
project_root = os.path.join(os.path.dirname(__file__), 'gamifikasi-paud-main')
sys.path.insert(0, project_root)
os.chdir(project_root)

from app import create_app, db
from app.models.question import Soal


app = create_app()

with app.app_context():
    rows = Soal.query.filter_by(kategori='huruf').limit(20).all()
    for row in rows:
        answer_letter = Soal.answer_key_to_letter(row.jawaban_benar)
        option_map = {
            'A': row.pilihan_a,
            'B': row.pilihan_b,
            'C': row.pilihan_c,
            'D': row.pilihan_d
        }
        answer_text = option_map.get(answer_letter, '').strip()
        img_preview = (row.image_question or '')[:100]
        print(f"ID {row.id}: Q=[{row.pertanyaan[:25]}] Ans=[{answer_text}]")
