#!/usr/bin/env python3
"""
Script untuk memeriksa dan memperbaiki soal game huruf.
Mengidentifikasi soal bermasalah, menghapus, dan mengganti dengan soal baru yang benar.
"""

import sys
import os
from datetime import datetime

# Navigasi ke direktori gamifikasi-paud-main
current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(current_dir, 'gamifikasi-paud-main')

sys.path.insert(0, project_dir)
os.chdir(project_dir)

from app import create_app, db
from app.models.question import Soal
from app.models.adventure_question_map import AdventureQuestionMap

app = create_app()

def check_huruf_questions():
    """Periksa semua soal huruf yang digunakan dalam game"""
    with app.app_context():
        print("=" * 80)
        print("PEMERIKSAAN SOAL GAME HURUF")
        print("=" * 80)
        
        # Ambil semua mapping untuk game huruf
        maps = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
            AdventureQuestionMap.level,
            AdventureQuestionMap.question_order
        ).all()
        
        print(f"\nTotal mapping untuk game huruf: {len(maps)}\n")
        
        problematic_questions = []
        
        for map_item in maps:
            if not map_item.question_id:
                print(f"❌ Level {map_item.level}, Order {map_item.question_order}: question_id kosong!")
                continue
                
            question = Soal.query.get(map_item.question_id)
            if not question:
                print(f"❌ Level {map_item.level}, Order {map_item.question_order}: Soal ID {map_item.question_id} tidak ditemukan!")
                problematic_questions.append(map_item)
                continue
            
            # Validasi soal
            errors = []
            
            # Cek kategori
            if question.kategori != 'huruf':
                errors.append(f"kategori='{question.kategori}' (harus 'huruf')")
            
            # Cek pertanyaan
            if not question.pertanyaan or not question.pertanyaan.strip():
                errors.append("pertanyaan kosong")
            
            # Cek pilihan - harus ada 4 pilihan
            pilihan_count = 0
            pilihan_list = []
            if question.pilihan_a:
                pilihan_count += 1
                pilihan_list.append(('A', question.pilihan_a))
            if question.pilihan_b:
                pilihan_count += 1
                pilihan_list.append(('B', question.pilihan_b))
            if question.pilihan_c:
                pilihan_count += 1
                pilihan_list.append(('C', question.pilihan_c))
            if question.pilihan_d:
                pilihan_count += 1
                pilihan_list.append(('D', question.pilihan_d))
            
            if pilihan_count != 4:
                errors.append(f"pilihan hanya ada {pilihan_count} (harus 4)")
            
            # Cek jawaban benar
            if not question.jawaban_benar or question.jawaban_benar.upper() not in ['A', 'B', 'C', 'D']:
                errors.append(f"jawaban_benar='{question.jawaban_benar}' (invalid)")
            else:
                # Verifikasi jawaban benar sesuai dengan pilihan yang ada
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
                    errors.append(f"jawaban_benar={jawaban_upper} tetapi pilihan_{jawaban_upper.lower()} kosong!")
            
            if errors:
                print(f"⚠️  Level {map_item.level}, Order {map_item.question_order} (ID: {question.id})")
                print(f"   Soal: {question.pertanyaan[:60]}")
                for error in errors:
                    print(f"   - {error}")
                print()
                problematic_questions.append(map_item)
            else:
                print(f"✓ Level {map_item.level}, Order {map_item.question_order} (ID: {question.id}): OK")
        
        print("\n" + "=" * 80)
        print(f"Total soal bermasalah: {len(problematic_questions)}")
        print("=" * 80)
        
        return problematic_questions


def create_replacement_questions():
    """Buat soal-soal pengganti yang benar dan lengkap"""
    
    replacement_questions = [
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'a',
            'pilihan_b': 'b',
            'pilihan_c': 'c',
            'pilihan_d': 'd',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'e',
            'pilihan_b': 'f',
            'pilihan_c': 'g',
            'pilihan_d': 'h',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'i',
            'pilihan_b': 'j',
            'pilihan_c': 'k',
            'pilihan_d': 'l',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'm',
            'pilihan_b': 'n',
            'pilihan_c': 'o',
            'pilihan_d': 'p',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'q',
            'pilihan_b': 'r',
            'pilihan_c': 's',
            'pilihan_d': 't',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'u',
            'pilihan_b': 'v',
            'pilihan_c': 'w',
            'pilihan_d': 'x',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'y',
            'pilihan_b': 'z',
            'pilihan_c': 'a',
            'pilihan_d': 'b',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'c',
            'pilihan_b': 'd',
            'pilihan_c': 'e',
            'pilihan_d': 'f',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'g',
            'pilihan_b': 'h',
            'pilihan_c': 'i',
            'pilihan_d': 'j',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'k',
            'pilihan_b': 'l',
            'pilihan_c': 'm',
            'pilihan_d': 'n',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
    ]
    
    return replacement_questions


def fix_huruf_game():
    """Perbaiki soal game huruf yang bermasalah"""
    with app.app_context():
        print("\n" + "=" * 80)
        print("PERBAIKAN SOAL GAME HURUF")
        print("=" * 80)
        
        # Identifikasi soal bermasalah
        problematic_maps = check_huruf_questions()
        
        if not problematic_maps:
            print("\n✓ Semua soal sudah benar! Tidak perlu perbaikan.")
            return True
        
        # Ambil soal pengganti
        replacements = create_replacement_questions()
        
        print(f"\nMenghapus {len(problematic_maps)} soal bermasalah dan menggantinya...")
        
        for idx, map_item in enumerate(problematic_maps):
            old_question_id = map_item.question_id
            
            # Hapus soal lama jika ada
            if old_question_id:
                old_question = Soal.query.get(old_question_id)
                if old_question:
                    db.session.delete(old_question)
                    print(f"✓ Menghapus soal lama ID {old_question_id}")
            
            # Buat soal baru
            replacement_data = replacements[idx % len(replacements)]
            new_question = Soal(
                kategori=replacement_data['kategori'],
                pertanyaan=replacement_data['pertanyaan'],
                pilihan_a=replacement_data['pilihan_a'],
                pilihan_b=replacement_data['pilihan_b'],
                pilihan_c=replacement_data['pilihan_c'],
                pilihan_d=replacement_data['pilihan_d'],
                jawaban_benar=replacement_data['jawaban_benar'],
                difficulty=replacement_data['difficulty'],
                question_type='text',
                use_in_adventure_map=True,
                use_in_daily_mission=False,
            )
            
            db.session.add(new_question)
            db.session.flush()  # Dapatkan ID baru
            
            # Update mapping
            map_item.question_id = new_question.id
            map_item.updated_at = datetime.utcnow()
            
            print(f"✓ Membuat soal baru ID {new_question.id} untuk Level {map_item.level}, Order {map_item.question_order}")
        
        # Simpan perubahan
        try:
            db.session.commit()
            print("\n✓ Semua perubahan berhasil disimpan ke database!")
            
            # Verifikasi
            print("\nVerifikasi perbaikan...")
            problematic_after = check_huruf_questions()
            if not problematic_after:
                print("\n✓✓✓ PERBAIKAN BERHASIL! Semua soal game huruf sudah benar!")
                return True
            else:
                print(f"\n⚠️  Masih ada {len(problematic_after)} soal yang bermasalah setelah perbaikan")
                return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat menyimpan: {e}")
            return False


if __name__ == '__main__':
    success = fix_huruf_game()
    sys.exit(0 if success else 1)
