#!/usr/bin/env python3
"""
Script untuk verifikasi final soal game huruf.
Memastikan semua soal sinkron dengan benar dan tidak ada kesalahan.
"""

import sys
import os

# Navigasi ke direktori gamifikasi-paud-main
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, 'gamifikasi-paud-main')

sys.path.insert(0, project_dir)
os.chdir(project_dir)

from app import create_app, db
from app.models.question import Soal
from app.models.adventure_question_map import AdventureQuestionMap

app = create_app()

def verify_final_huruf_game():
    """Verifikasi final bahwa semua soal game huruf sudah benar"""
    with app.app_context():
        print("=" * 100)
        print("VERIFIKASI FINAL GAME HURUF")
        print("=" * 100)
        
        # Ambil semua mapping
        maps = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
            AdventureQuestionMap.level,
            AdventureQuestionMap.question_order
        ).all()
        
        print(f"\nTotal soal dalam game huruf: {len(maps)}")
        
        # Statistik
        stats = {
            'total': len(maps),
            'valid': 0,
            'invalid': 0,
            'missing_question': 0,
            'wrong_category': 0,
            'incomplete_choices': 0,
            'invalid_answer': 0,
            'answer_mismatch': 0,
        }
        
        valid_questions = []
        
        for map_item in maps:
            if not map_item.question_id:
                stats['missing_question'] += 1
                stats['invalid'] += 1
                continue
                
            question = Soal.query.get(map_item.question_id)
            if not question:
                stats['missing_question'] += 1
                stats['invalid'] += 1
                continue
            
            # Validasi kategori
            if question.kategori != 'huruf':
                stats['wrong_category'] += 1
                stats['invalid'] += 1
                continue
            
            # Validasi pilihan
            pilihan_count = sum([
                bool(question.pilihan_a),
                bool(question.pilihan_b),
                bool(question.pilihan_c),
                bool(question.pilihan_d)
            ])
            if pilihan_count != 4:
                stats['incomplete_choices'] += 1
                stats['invalid'] += 1
                continue
            
            # Validasi jawaban
            if not question.jawaban_benar or question.jawaban_benar.upper() not in ['A', 'B', 'C', 'D']:
                stats['invalid_answer'] += 1
                stats['invalid'] += 1
                continue
            
            # Validasi konsistensi jawaban
            jawaban_upper = question.jawaban_benar.upper()
            jawaban_text = None
            if jawaban_upper == 'A':
                jawaban_text = question.pilihan_a
            elif jawaban_upper == 'B':
                jawaban_text = question.pilihan_b
            elif jawaban_upper == 'C':
                jawaban_text = question.pilihan_c
            elif jawaban_upper == 'D':
                jawaban_text = question.pilihan_d
            
            if not jawaban_text:
                stats['answer_mismatch'] += 1
                stats['invalid'] += 1
                continue
            
            # Soal valid
            stats['valid'] += 1
            valid_questions.append({
                'id': question.id,
                'level': map_item.level,
                'order': map_item.question_order,
                'pertanyaan': question.pertanyaan[:50],
                'jawaban_benar': question.jawaban_benar,
            })
        
        # Tampilkan hasil
        print("\n" + "=" * 100)
        print("HASIL VERIFIKASI")
        print("=" * 100)
        
        print(f"\nTotal soal: {stats['total']}")
        print(f"✓ Soal valid: {stats['valid']}")
        print(f"✗ Soal invalid: {stats['invalid']}")
        
        if stats['invalid'] > 0:
            print("\nDetail masalah:")
            if stats['missing_question'] > 0:
                print(f"  - Soal tidak ditemukan: {stats['missing_question']}")
            if stats['wrong_category'] > 0:
                print(f"  - Kategori salah: {stats['wrong_category']}")
            if stats['incomplete_choices'] > 0:
                print(f"  - Pilihan tidak lengkap: {stats['incomplete_choices']}")
            if stats['invalid_answer'] > 0:
                print(f"  - Jawaban tidak valid: {stats['invalid_answer']}")
            if stats['answer_mismatch'] > 0:
                print(f"  - Jawaban tidak sesuai pilihan: {stats['answer_mismatch']}")
        
        # Tampilkan daftar soal valid
        print("\n" + "=" * 100)
        print("DAFTAR SOAL VALID")
        print("=" * 100 + "\n")
        
        for idx, q in enumerate(valid_questions, 1):
            print(f"{idx:2d}. Level {q['level']}, Order {q['order']} (ID: {q['id']})")
            print(f"    Soal: {q['pertanyaan']}...")
            print(f"    Jawaban: {q['jawaban_benar']}")
        
        # Hasil akhir
        print("\n" + "=" * 100)
        if stats['invalid'] == 0:
            print("✓✓✓ VERIFIKASI BERHASIL! Semua soal game huruf sudah benar dan sinkron!")
            print("=" * 100)
            return True
        else:
            print("✗ VERIFIKASI GAGAL! Masih ada soal yang bermasalah.")
            print("=" * 100)
            return False


if __name__ == '__main__':
    success = verify_final_huruf_game()
    sys.exit(0 if success else 1)
