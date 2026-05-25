#!/usr/bin/env python3
"""
Script untuk membuat soal Game Huruf A-Z yang sesuai untuk anak TK/PAUD.
Setiap soal fokus pada satu huruf dengan kata-kata sederhana dan familiar untuk anak-anak.
"""

import sys
import os
import random
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

# Soal A-Z untuk anak TK/PAUD
PAUD_ALPHABET_QUESTIONS = [
    # Huruf A
    {
        'huruf': 'A',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf A.',
        'pilihan_a': 'Apel',
        'pilihan_b': 'Buku',
        'pilihan_c': 'Matahari',
        'pilihan_d': 'Zebra',
        'jawaban_benar': 'A',
    },
    # Huruf B
    {
        'huruf': 'B',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf B.',
        'pilihan_a': 'Apel',
        'pilihan_b': 'Bola',
        'pilihan_c': 'Rumah',
        'pilihan_d': 'Mobil',
        'jawaban_benar': 'B',
    },
    # Huruf C
    {
        'huruf': 'C',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf C.',
        'pilihan_a': 'Buku',
        'pilihan_b': 'Ayam',
        'pilihan_c': 'Cangkul',
        'pilihan_d': 'Boneka',
        'jawaban_benar': 'C',
    },
    # Huruf D
    {
        'huruf': 'D',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf D.',
        'pilihan_a': 'Kucing',
        'pilihan_b': 'Dadu',
        'pilihan_c': 'Ikan',
        'pilihan_d': 'Sapu',
        'jawaban_benar': 'B',
    },
    # Huruf E
    {
        'huruf': 'E',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf E.',
        'pilihan_a': 'Ekor',
        'pilihan_b': 'Rumah',
        'pilihan_c': 'Boneka',
        'pilihan_d': 'Meja',
        'jawaban_benar': 'A',
    },
    # Huruf F
    {
        'huruf': 'F',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf F.',
        'pilihan_a': 'Kotak',
        'pilihan_b': 'Sendok',
        'pilihan_c': 'Foto',
        'pilihan_d': 'Topi',
        'jawaban_benar': 'C',
    },
    # Huruf G
    {
        'huruf': 'G',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf G.',
        'pilihan_a': 'Gajah',
        'pilihan_b': 'Burung',
        'pilihan_c': 'Pisang',
        'pilihan_d': 'Kepala',
        'jawaban_benar': 'A',
    },
    # Huruf H
    {
        'huruf': 'H',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf H.',
        'pilihan_a': 'Tas',
        'pilihan_b': 'Helm',
        'pilihan_c': 'Kaki',
        'pilihan_d': 'Bulan',
        'jawaban_benar': 'B',
    },
    # Huruf I
    {
        'huruf': 'I',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf I.',
        'pilihan_a': 'Mainan',
        'pilihan_b': 'Ikan',
        'pilihan_c': 'Rumah',
        'pilihan_d': 'Pohon',
        'jawaban_benar': 'B',
    },
    # Huruf J
    {
        'huruf': 'J',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf J.',
        'pilihan_a': 'Jembatan',
        'pilihan_b': 'Kuda',
        'pilihan_c': 'Lilin',
        'pilihan_d': 'Sendok',
        'jawaban_benar': 'A',
    },
    # Huruf K
    {
        'huruf': 'K',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf K.',
        'pilihan_a': 'Meja',
        'pilihan_b': 'Kucing',
        'pilihan_c': 'Piring',
        'pilihan_d': 'Buku',
        'jawaban_benar': 'B',
    },
    # Huruf L
    {
        'huruf': 'L',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf L.',
        'pilihan_a': 'Gelas',
        'pilihan_b': 'Lilin',
        'pilihan_c': 'Mainan',
        'pilihan_d': 'Pohon',
        'jawaban_benar': 'B',
    },
    # Huruf M
    {
        'huruf': 'M',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf M.',
        'pilihan_a': 'Mobil',
        'pilihan_b': 'Tas',
        'pilihan_c': 'Bulan',
        'pilihan_d': 'Rumah',
        'jawaban_benar': 'A',
    },
    # Huruf N
    {
        'huruf': 'N',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf N.',
        'pilihan_a': 'Buku',
        'pilihan_b': 'Nanas',
        'pilihan_c': 'Meja',
        'pilihan_d': 'Kupu-kupu',
        'jawaban_benar': 'B',
    },
    # Huruf O
    {
        'huruf': 'O',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf O.',
        'pilihan_a': 'Obat',
        'pilihan_b': 'Roti',
        'pilihan_c': 'Mainan',
        'pilihan_d': 'Rumah',
        'jawaban_benar': 'A',
    },
    # Huruf P
    {
        'huruf': 'P',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf P.',
        'pilihan_a': 'Kupu-kupu',
        'pilihan_b': 'Meja',
        'pilihan_c': 'Pisang',
        'pilihan_d': 'Susu',
        'jawaban_benar': 'C',
    },
    # Huruf Q
    {
        'huruf': 'Q',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf Q.',
        'pilihan_a': 'Roti',
        'pilihan_b': 'Qanun',
        'pilihan_c': 'Mainan',
        'pilihan_d': 'Pohon',
        'jawaban_benar': 'B',
    },
    # Huruf R
    {
        'huruf': 'R',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf R.',
        'pilihan_a': 'Mainan',
        'pilihan_b': 'Rumah',
        'pilihan_c': 'Kupu-kupu',
        'pilihan_d': 'Sendok',
        'jawaban_benar': 'B',
    },
    # Huruf S
    {
        'huruf': 'S',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf S.',
        'pilihan_a': 'Roti',
        'pilihan_b': 'Tanah',
        'pilihan_c': 'Susu',
        'pilihan_d': 'Mainan',
        'jawaban_benar': 'C',
    },
    # Huruf T
    {
        'huruf': 'T',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf T.',
        'pilihan_a': 'Tangan',
        'pilihan_b': 'Roti',
        'pilihan_c': 'Buku',
        'pilihan_d': 'Susu',
        'jawaban_benar': 'A',
    },
    # Huruf U
    {
        'huruf': 'U',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf U.',
        'pilihan_a': 'Ubur-ubur',
        'pilihan_b': 'Susu',
        'pilihan_c': 'Roti',
        'pilihan_d': 'Mobil',
        'jawaban_benar': 'A',
    },
    # Huruf V
    {
        'huruf': 'V',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf V.',
        'pilihan_a': 'Buku',
        'pilihan_b': 'Vas',
        'pilihan_c': 'Roti',
        'pilihan_d': 'Mainan',
        'jawaban_benar': 'B',
    },
    # Huruf W
    {
        'huruf': 'W',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf W.',
        'pilihan_a': 'Roti',
        'pilihan_b': 'Warna',
        'pilihan_c': 'Buku',
        'pilihan_d': 'Pohon',
        'jawaban_benar': 'B',
    },
    # Huruf X
    {
        'huruf': 'X',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf X.',
        'pilihan_a': 'Xilofon',
        'pilihan_b': 'Roti',
        'pilihan_c': 'Susu',
        'pilihan_d': 'Mainan',
        'jawaban_benar': 'A',
    },
    # Huruf Y
    {
        'huruf': 'Y',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf Y.',
        'pilihan_a': 'Buku',
        'pilihan_b': 'Yoyo',
        'pilihan_c': 'Roti',
        'pilihan_d': 'Mobil',
        'jawaban_benar': 'B',
    },
    # Huruf Z
    {
        'huruf': 'Z',
        'pertanyaan': 'Pilih kata yang dimulai dengan huruf Z.',
        'pilihan_a': 'Roti',
        'pilihan_b': 'Mainan',
        'pilihan_c': 'Zebra',
        'pilihan_d': 'Susu',
        'jawaban_benar': 'C',
    },
]


def create_paud_alphabet_questions():
    """Buat soal huruf A-Z yang sesuai untuk anak TK/PAUD"""
    return PAUD_ALPHABET_QUESTIONS


def replace_with_paud_alphabet_questions():
    """Ganti semua soal huruf dengan soal A-Z PAUD yang baru"""
    with app.app_context():
        print("=" * 100)
        print("PEMBUATAN SOAL GAME HURUF A-Z UNTUK ANAK TK/PAUD")
        print("=" * 100)
        
        # Ambil semua mapping
        maps = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
            AdventureQuestionMap.level,
            AdventureQuestionMap.question_order
        ).all()
        
        print(f"\nTotal slot untuk game huruf: {len(maps)}")
        print(f"Total soal A-Z yang tersedia: {len(PAUD_ALPHABET_QUESTIONS)}")
        
        # Buat random order dari soal A-Z
        question_pool = PAUD_ALPHABET_QUESTIONS.copy()
        random.shuffle(question_pool)
        
        # Jika ada slot lebih, cycle kembali
        if len(maps) > len(question_pool):
            random.shuffle(question_pool)
            question_pool_extended = question_pool.copy()
            while len(question_pool_extended) < len(maps):
                additional = PAUD_ALPHABET_QUESTIONS.copy()
                random.shuffle(additional)
                question_pool_extended.extend(additional[:len(maps) - len(question_pool_extended)])
            question_pool = question_pool_extended
        
        print(f"\nMengganti {len(maps)} soal huruf dengan soal A-Z acak untuk PAUD...\n")
        
        replaced_count = 0
        
        for idx, map_item in enumerate(maps):
            # Hapus soal lama
            if map_item.question_id:
                old_question = Soal.query.get(map_item.question_id)
                if old_question:
                    db.session.delete(old_question)
                    print(f"[{idx + 1:2d}] Menghapus soal lama ID {old_question.id}")
            
            # Ambil soal dari pool
            question_data = question_pool[idx]
            
            # Tentukan kesulitan berdasarkan level
            level = map_item.level
            if level <= 2:
                difficulty = 'mudah'
            elif level <= 3:
                difficulty = 'sedang'
            else:
                difficulty = 'sulit'
            
            # Buat soal baru
            new_question = Soal(
                kategori='huruf',
                pertanyaan=question_data['pertanyaan'],
                pilihan_a=question_data['pilihan_a'],
                pilihan_b=question_data['pilihan_b'],
                pilihan_c=question_data['pilihan_c'],
                pilihan_d=question_data['pilihan_d'],
                jawaban_benar=question_data['jawaban_benar'],
                difficulty=difficulty,
                question_type='text',
                use_in_adventure_map=True,
                use_in_daily_mission=False,
            )
            
            db.session.add(new_question)
            db.session.flush()
            
            # Update mapping
            map_item.question_id = new_question.id
            map_item.updated_at = datetime.utcnow()
            
            huruf_info = question_data.get('huruf', '?')
            print(f"[{idx + 1:2d}] Level {map_item.level}, Order {map_item.question_order}: Huruf {huruf_info} (ID: {new_question.id})")
            replaced_count += 1
        
        # Simpan perubahan
        try:
            db.session.commit()
            print(f"\n✓ {replaced_count} soal berhasil dibuat dan disimpan ke database!")
            
            # Verifikasi
            print("\n" + "=" * 100)
            print("VERIFIKASI SOAL A-Z YANG BARU")
            print("=" * 100 + "\n")
            
            maps_after = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
                AdventureQuestionMap.level,
                AdventureQuestionMap.question_order
            ).all()
            
            valid_count = 0
            invalid_count = 0
            
            for idx, map_item in enumerate(maps_after, 1):
                question = Soal.query.get(map_item.question_id)
                if not question:
                    print(f"❌ [{idx:2d}] Soal tidak ditemukan!")
                    invalid_count += 1
                    continue
                
                # Validasi
                errors = []
                if question.kategori != 'huruf':
                    errors.append(f"kategori='{question.kategori}'")
                
                pilihan_count = sum([
                    bool(question.pilihan_a),
                    bool(question.pilihan_b),
                    bool(question.pilihan_c),
                    bool(question.pilihan_d)
                ])
                if pilihan_count != 4:
                    errors.append(f"pilihan hanya {pilihan_count}")
                
                if not question.jawaban_benar or question.jawaban_benar.upper() not in ['A', 'B', 'C', 'D']:
                    errors.append(f"jawaban '{question.jawaban_benar}'")
                else:
                    jawaban_upper = question.jawaban_benar.upper()
                    if jawaban_upper == 'A':
                        jawaban_text = question.pilihan_a
                    elif jawaban_upper == 'B':
                        jawaban_text = question.pilihan_b
                    elif jawaban_upper == 'C':
                        jawaban_text = question.pilihan_c
                    else:
                        jawaban_text = question.pilihan_d
                    
                    if not jawaban_text:
                        errors.append(f"jawaban {jawaban_upper} kosong")
                
                if errors:
                    print(f"❌ [{idx:2d}] Level {map_item.level}, Order {map_item.question_order}: {', '.join(errors)}")
                    invalid_count += 1
                else:
                    print(f"✓ [{idx:2d}] Level {map_item.level}, Order {map_item.question_order}: {question.pertanyaan[:60]}")
                    valid_count += 1
            
            print("\n" + "=" * 100)
            print(f"Total soal valid: {valid_count}")
            print(f"Total soal invalid: {invalid_count}")
            print("=" * 100)
            
            if invalid_count == 0:
                print("\n✓✓✓ BERHASIL! Semua soal huruf A-Z sudah dibuat dengan benar!")
                return True
            else:
                print(f"\n⚠️  Ada {invalid_count} soal yang masih bermasalah")
                return False
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat menyimpan: {e}")
            return False


if __name__ == '__main__':
    success = replace_with_paud_alphabet_questions()
    sys.exit(0 if success else 1)
