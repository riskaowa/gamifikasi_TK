#!/usr/bin/env python3
"""
Script untuk memeriksa dan memperbaiki peta pertualangan huruf.
Memastikan soal-soal dari Adventure Map menggunakan soal huruf yang baru.
"""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'gamifikasi-paud-main')
sys.path.insert(0, app_dir)

from app import create_app, db
from app.models.adventure_question_map import AdventureQuestionMap
from app.models.question import Soal

app = create_app()

def check_and_rebuild_adventure_map():
    with app.app_context():
        print("PEMERIKSAAN PETA PERTUALANGAN HURUF")
        print("="*80)
        
        # Periksa berapa soal huruf yang ada
        huruf_count = Soal.query.filter_by(kategori='huruf').count()
        print(f"\nTotal soal huruf di database: {huruf_count}")
        
        # Periksa adventure map untuk huruf
        adventure_huruf = AdventureQuestionMap.query.filter_by(game_key='huruf').all()
        print(f"Total entry di Adventure Map (huruf): {len(adventure_huruf)}")
        
        # Lihat soal-soal yang direferensikan
        print("\nSoal-soal yang direferensikan di Adventure Map:")
        question_ids = set()
        for entry in adventure_huruf:
            question_ids.add(entry.question_id)
        
        print(f"Unique question IDs: {len(question_ids)}")
        
        # Cek apakah soal tersebut masih ada
        valid_ids = 0
        invalid_ids = 0
        for qid in question_ids:
            soal = Soal.query.get(qid)
            if soal:
                valid_ids += 1
            else:
                invalid_ids += 1
        
        print(f"Valid question IDs: {valid_ids}")
        print(f"Invalid/Missing question IDs: {invalid_ids}")
        
        # Sample soal dari adventure map
        if adventure_huruf:
            print(f"\nSample entry dari Adventure Map:")
            for entry in adventure_huruf[:3]:
                soal = Soal.query.get(entry.question_id) if entry.question_id else None
                print(f"  Level {entry.level}, Order {entry.question_order}:")
                if soal:
                    print(f"    Question ID: {entry.question_id}")
                    print(f"    Kategori: {soal.kategori}")
                    print(f"    Pertanyaan: {soal.pertanyaan}")
                    print(f"    Jawaban: {soal.jawaban_benar}")
                else:
                    print(f"    Question ID {entry.question_id} - NOT FOUND")
        
        # Hapus dan rebuild adventure map
        print("\n" + "="*80)
        print("REBUILD ADVENTURE MAP")
        print("="*80)
        
        old_count = AdventureQuestionMap.query.filter_by(game_key='huruf').count()
        AdventureQuestionMap.query.filter_by(game_key='huruf').delete()
        db.session.commit()
        print(f"\n✓ {old_count} entry adventure map huruf dihapus")
        
        # Buat ulang
        from app.routes import ensure_adventure_question_map, HURUF_LEVEL_RULES
        
        print(f"Membuat ulang adventure map...")
        slots = ensure_adventure_question_map('huruf', HURUF_LEVEL_RULES)
        print(f"✓ {len(slots)} slot adventure map dibuat")
        
        # Verifikasi ulang
        print(f"\nVerifikasi ulang:")
        adventure_huruf_baru = AdventureQuestionMap.query.filter_by(game_key='huruf').all()
        print(f"Total entry di Adventure Map (huruf): {len(adventure_huruf_baru)}")
        
        # Sample soal baru
        print(f"\nSample soal dari adventure map baru:")
        soal_samples = []
        for entry in sorted(adventure_huruf_baru, key=lambda x: (x.level, x.question_order))[:6]:
            soal = Soal.query.get(entry.question_id)
            if soal:
                soal_samples.append({
                    'level': entry.level,
                    'order': entry.question_order,
                    'pertanyaan': soal.pertanyaan,
                    'jawaban': soal.jawaban_benar,
                })
        
        for sample in soal_samples:
            print(f"  Level {sample['level']}, Order {sample['order']}: {sample['pertanyaan']}")
            print(f"    Jawaban: {sample['jawaban']}")
        
        return len(slots)

if __name__ == '__main__':
    result = check_and_rebuild_adventure_map()
    print("\n" + "="*80)
    print(f"✓ Peta pertualangan huruf telah diperbaharui dengan {result} slot")
