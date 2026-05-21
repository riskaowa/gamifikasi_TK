#!/usr/bin/env python3
"""
Script untuk detail check dan perbaikan soal game huruf.
Menampilkan detail setiap soal dan validasi lengkap.
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

def show_detailed_huruf_questions():
    """Tampilkan semua soal huruf dengan detail lengkap"""
    with app.app_context():
        print("=" * 120)
        print("DETAIL LENGKAP SEMUA SOAL GAME HURUF")
        print("=" * 120)
        
        # Ambil semua mapping untuk game huruf
        maps = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
            AdventureQuestionMap.level,
            AdventureQuestionMap.question_order
        ).all()
        
        print(f"\nTotal mapping untuk game huruf: {len(maps)}\n")
        
        for idx, map_item in enumerate(maps, 1):
            print(f"\n{idx}. Level {map_item.level}, Order {map_item.question_order}")
            print("   " + "-" * 80)
            
            if not map_item.question_id:
                print("   ❌ ERROR: question_id kosong!")
                continue
                
            question = Soal.query.get(map_item.question_id)
            if not question:
                print(f"   ❌ ERROR: Soal ID {map_item.question_id} tidak ditemukan di database!")
                continue
            
            print(f"   ID Soal: {question.id}")
            print(f"   Kategori: {question.kategori}")
            print(f"   Pertanyaan: {question.pertanyaan}")
            print(f"   Pilihan A: {question.pilihan_a}")
            print(f"   Pilihan B: {question.pilihan_b}")
            print(f"   Pilihan C: {question.pilihan_c}")
            print(f"   Pilihan D: {question.pilihan_d}")
            print(f"   Jawaban Benar: {question.jawaban_benar}")
            print(f"   Difficulty: {question.difficulty}")
            print(f"   Has Image: {bool(question.image_question)}")
            
            # Validasi
            errors = []
            
            if question.kategori != 'huruf':
                errors.append(f"✗ Kategori '{question.kategori}' (harus 'huruf')")
            
            if not question.pertanyaan:
                errors.append("✗ Pertanyaan kosong")
            
            pilihan_count = sum([
                bool(question.pilihan_a),
                bool(question.pilihan_b),
                bool(question.pilihan_c),
                bool(question.pilihan_d)
            ])
            if pilihan_count != 4:
                errors.append(f"✗ Hanya {pilihan_count} pilihan (harus 4)")
            
            if not question.jawaban_benar or question.jawaban_benar.upper() not in ['A', 'B', 'C', 'D']:
                errors.append(f"✗ Jawaban '{question.jawaban_benar}' tidak valid")
            else:
                # Cek konsistensi jawaban
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
                    errors.append(f"✗ Jawaban {jawaban_upper} kosong!")
            
            if errors:
                print("   ⚠️  MASALAH DITEMUKAN:")
                for error in errors:
                    print(f"       {error}")
            else:
                print("   ✓ SEMUA BAIK")


def get_new_huruf_questions():
    """Buat daftar soal huruf baru yang benar dan bervariasi"""
    return [
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Apel',
            'pilihan_b': 'Bola',
            'pilihan_c': 'Cangkul',
            'pilihan_d': 'Drum',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Topi',
            'pilihan_b': 'Ubur-ubur',
            'pilihan_c': 'Vas',
            'pilihan_d': 'Walau',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Xilofon',
            'pilihan_b': 'Yoyo',
            'pilihan_c': 'Zebra',
            'pilihan_d': 'Apel',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Buku',
            'pilihan_b': 'Cicak',
            'pilihan_c': 'Dada',
            'pilihan_d': 'Ekor',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Gajah',
            'pilihan_b': 'Hasil',
            'pilihan_c': 'Ibu',
            'pilihan_d': 'Jari',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'mudah',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Kaca',
            'pilihan_b': 'Lemon',
            'pilihan_c': 'Mobil',
            'pilihan_d': 'Nasi',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Obat',
            'pilihan_b': 'Palu',
            'pilihan_c': 'Rumah',
            'pilihan_d': 'Sapu',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Telur',
            'pilihan_b': 'Udang',
            'pilihan_c': 'Wayang',
            'pilihan_d': 'Yoga',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sedang',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Zucchini',
            'pilihan_b': 'Awan',
            'pilihan_c': 'Buku',
            'pilihan_d': 'Candi',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Dinding',
            'pilihan_b': 'Ember',
            'pilihan_c': 'Fajar',
            'pilihan_d': 'Gita',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Hutan',
            'pilihan_b': 'Ikat',
            'pilihan_c': 'Jerat',
            'pilihan_d': 'Kapal',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Laut',
            'pilihan_b': 'Macan',
            'pilihan_c': 'Natif',
            'pilihan_d': 'Oasis',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Padi',
            'pilihan_b': 'Rajah',
            'pilihan_c': 'Sapi',
            'pilihan_d': 'Taman',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Ulama',
            'pilihan_b': 'Vaksin',
            'pilihan_c': 'Warna',
            'pilihan_d': 'X-Ray',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Yogurt',
            'pilihan_b': 'Zaman',
            'pilihan_c': 'Abjad',
            'pilihan_d': 'Balon',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Cita',
            'pilihan_b': 'Duit',
            'pilihan_c': 'Engkau',
            'pilihan_d': 'Fakta',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Guna',
            'pilihan_b': 'Halus',
            'pilihan_c': 'Istana',
            'pilihan_d': 'Juara',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Kerja',
            'pilihan_b': 'Listrik',
            'pilihan_c': 'Makanan',
            'pilihan_d': 'Naga',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Oleh',
            'pilihan_b': 'Pergi',
            'pilihan_c': 'Roti',
            'pilihan_d': 'Sampit',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Temu',
            'pilihan_b': 'Usia',
            'pilihan_c': 'Vonis',
            'pilihan_d': 'Wajib',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Xanadu',
            'pilihan_b': 'Yayasan',
            'pilihan_c': 'Zebroid',
            'pilihan_d': 'Abadi',
            'jawaban_benar': 'A',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Bacaan',
            'pilihan_b': 'Catatan',
            'pilihan_c': 'Dada',
            'pilihan_d': 'Edan',
            'jawaban_benar': 'B',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Fokus',
            'pilihan_b': 'Gores',
            'pilihan_c': 'Habis',
            'pilihan_d': 'Ikon',
            'jawaban_benar': 'C',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
        {
            'pertanyaan': 'Pilih huruf yang sesuai gambar.',
            'pilihan_a': 'Jangan',
            'pilihan_b': 'Kabar',
            'pilihan_c': 'Lakuan',
            'pilihan_d': 'Masak',
            'jawaban_benar': 'D',
            'kategori': 'huruf',
            'difficulty': 'sulit',
        },
    ]


def replace_huruf_questions():
    """Ganti semua soal huruf dengan soal baru yang benar dan bervariasi"""
    with app.app_context():
        print("\n" + "=" * 120)
        print("PENGGANTIAN SOAL GAME HURUF DENGAN SOAL BARU")
        print("=" * 120)
        
        # Tampilkan status awal
        show_detailed_huruf_questions()
        
        # Ambil semua mapping
        maps = AdventureQuestionMap.query.filter_by(game_key='huruf').order_by(
            AdventureQuestionMap.level,
            AdventureQuestionMap.question_order
        ).all()
        
        print(f"\n\nMengganti {len(maps)} soal huruf dengan soal baru yang benar...\n")
        
        # Ambil soal pengganti
        replacements = get_new_huruf_questions()
        
        replaced_count = 0
        
        for idx, map_item in enumerate(maps):
            # Hapus soal lama
            if map_item.question_id:
                old_question = Soal.query.get(map_item.question_id)
                if old_question:
                    db.session.delete(old_question)
                    print(f"[{idx + 1:2d}] Menghapus soal lama ID {old_question.id}")
            
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
            db.session.flush()
            
            # Update mapping
            map_item.question_id = new_question.id
            map_item.updated_at = datetime.utcnow()
            
            print(f"[{idx + 1:2d}] Membuat soal baru ID {new_question.id}: {replacement_data['pilihan_a']}")
            replaced_count += 1
        
        # Simpan perubahan
        try:
            db.session.commit()
            print(f"\n✓ {replaced_count} soal berhasil diganti dan disimpan ke database!")
            
            # Verifikasi
            print("\n" + "=" * 120)
            print("VERIFIKASI SOAL SETELAH PENGGANTIAN")
            print("=" * 120)
            show_detailed_huruf_questions()
            
            print("\n✓✓✓ PENGGANTIAN SOAL BERHASIL! Semua soal game huruf sudah diganti dengan soal baru.")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error saat menyimpan: {e}")
            return False


if __name__ == '__main__':
    success = replace_huruf_questions()
    sys.exit(0 if success else 1)
